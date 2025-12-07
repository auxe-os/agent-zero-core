import asyncio
from dataclasses import dataclass
import threading
from concurrent.futures import Future
from typing import Any, Callable, Optional, Coroutine, TypeVar, Awaitable

T = TypeVar("T")

class EventLoopThread:
    """A singleton class that manages a background event loop thread."""
    _instances = {}
    _lock = threading.Lock()

    def __init__(self, thread_name: str = "Background") -> None:
        """Initializes the event loop thread.

        Args:
            thread_name: The name of the thread.
        """
        self.thread_name = thread_name
        self._start()

    def __new__(cls, thread_name: str = "Background"):
        """Creates a new instance of the EventLoopThread if one does not already
        exist for the given thread name.
        """
        with cls._lock:
            if thread_name not in cls._instances:
                instance = super(EventLoopThread, cls).__new__(cls)
                cls._instances[thread_name] = instance
            return cls._instances[thread_name]

    def _start(self):
        """Starts the event loop thread."""
        if not hasattr(self, "loop") or not self.loop:
            self.loop = asyncio.new_event_loop()
        if not hasattr(self, "thread") or not self.thread:
            self.thread = threading.Thread(
                target=self._run_event_loop, daemon=True, name=self.thread_name
            )
            self.thread.start()

    def _run_event_loop(self):
        """Runs the event loop."""
        if not self.loop:
            raise RuntimeError("Event loop is not initialized")
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def terminate(self):
        """Terminates the event loop thread."""
        if self.loop and self.loop.is_running():
            self.loop.stop()
        self.loop = None
        self.thread = None

    def run_coroutine(self, coro):
        """Runs a coroutine in the event loop thread.

        Args:
            coro: The coroutine to run.

        Returns:
            A future that can be used to get the result of the coroutine.
        """
        self._start()
        if not self.loop:
            raise RuntimeError("Event loop is not initialized")
        return asyncio.run_coroutine_threadsafe(coro, self.loop)


@dataclass
class ChildTask:
    """Represents a child task of a DeferredTask."""
    task: "DeferredTask"
    terminate_thread: bool


class DeferredTask:
    """A class for running a coroutine in a background thread."""
    def __init__(
        self,
        thread_name: str = "Background",
    ):
        """Initializes a DeferredTask.

        Args:
            thread_name: The name of the background thread.
        """
        self.event_loop_thread = EventLoopThread(thread_name)
        self._future: Optional[Future] = None
        self.children: list[ChildTask] = []

    def start_task(
        self, func: Callable[..., Coroutine[Any, Any, Any]], *args: Any, **kwargs: Any
    ):
        """Starts the task.

        Args:
            func: The coroutine function to run.
            *args: The positional arguments to pass to the function.
            **kwargs: The keyword arguments to pass to the function.

        Returns:
            The DeferredTask instance.
        """
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._start_task()
        return self

    def __del__(self):
        self.kill()

    def _start_task(self):
        self._future = self.event_loop_thread.run_coroutine(self._run())

    async def _run(self):
        return await self.func(*self.args, **self.kwargs)

    def is_ready(self) -> bool:
        """Checks if the task is finished.

        Returns:
            True if the task is finished, False otherwise.
        """
        return self._future.done() if self._future else False

    def result_sync(self, timeout: Optional[float] = None) -> Any:
        """Gets the result of the task synchronously.

        Args:
            timeout: The maximum time to wait for the result.

        Returns:
            The result of the task.
        """
        if not self._future:
            raise RuntimeError("Task hasn't been started")
        try:
            return self._future.result(timeout)
        except TimeoutError:
            raise TimeoutError(
                "The task did not complete within the specified timeout."
            )

    async def result(self, timeout: Optional[float] = None) -> Any:
        """Gets the result of the task asynchronously.

        Args:
            timeout: The maximum time to wait for the result.

        Returns:
            The result of the task.
        """
        if not self._future:
            raise RuntimeError("Task hasn't been started")

        loop = asyncio.get_running_loop()

        def _get_result():
            try:
                result = self._future.result(timeout)  # type: ignore
                # self.kill()
                return result
            except TimeoutError:
                raise TimeoutError(
                    "The task did not complete within the specified timeout."
                )

        return await loop.run_in_executor(None, _get_result)

    def kill(self, terminate_thread: bool = False) -> None:
        """Kills the task and optionally terminates its thread.

        Args:
            terminate_thread: Whether to terminate the thread.
        """
        self.kill_children()
        if self._future and not self._future.done():
            self._future.cancel()

        if (
            terminate_thread
            and self.event_loop_thread.loop
            and self.event_loop_thread.loop.is_running()
        ):

            def cleanup():
                tasks = [
                    t
                    for t in asyncio.all_tasks(self.event_loop_thread.loop)
                    if t is not asyncio.current_task(self.event_loop_thread.loop)
                ]
                for task in tasks:
                    task.cancel()
                    try:
                        # Give tasks a chance to cleanup
                        if self.event_loop_thread.loop:
                            self.event_loop_thread.loop.run_until_complete(
                                asyncio.gather(task, return_exceptions=True)
                            )
                    except Exception:
                        pass  # Ignore cleanup errors

            self.event_loop_thread.loop.call_soon_threadsafe(cleanup)
            self.event_loop_thread.terminate()

    def kill_children(self) -> None:
        """Kills all child tasks."""
        for child in self.children:
            child.task.kill(terminate_thread=child.terminate_thread)
        self.children = []

    def is_alive(self) -> bool:
        """Checks if the task is still running.

        Returns:
            True if the task is running, False otherwise.
        """
        return self._future and not self._future.done()  # type: ignore

    def restart(self, terminate_thread: bool = False) -> None:
        """Restarts the task.

        Args:
            terminate_thread: Whether to terminate the thread.
        """
        self.kill(terminate_thread=terminate_thread)
        self._start_task()

    def add_child_task(
        self, task: "DeferredTask", terminate_thread: bool = False
    ) -> None:
        """Adds a child task.

        Args:
            task: The child task to add.
            terminate_thread: Whether to terminate the child's thread when
                              the parent is killed.
        """
        self.children.append(ChildTask(task, terminate_thread))

    async def _execute_in_task_context(
        self, func: Callable[..., T], *args, **kwargs
    ) -> T:
        """Executes a function in the task's context and returns its result."""
        result = func(*args, **kwargs)
        if asyncio.iscoroutine(result):
            return await result
        return result

    def execute_inside(self, func: Callable[..., T], *args, **kwargs) -> Awaitable[T]:
        """Executes a function inside the task's event loop.

        Args:
            func: The function to execute.
            *args: The positional arguments to pass to the function.
            **kwargs: The keyword arguments to pass to the function.

        Returns:
            An awaitable that resolves to the result of the function.
        """
        if not self.event_loop_thread.loop:
            raise RuntimeError("Event loop is not initialized")

        future: Future = Future()

        async def wrapped():
            if not self.event_loop_thread.loop:
                raise RuntimeError("Event loop is not initialized")
            try:
                result = await self._execute_in_task_context(func, *args, **kwargs)
                # Keep awaiting until we get a concrete value
                while isinstance(result, Awaitable):
                    result = await result
                self.event_loop_thread.loop.call_soon_threadsafe(
                    future.set_result, result
                )
            except Exception as e:
                self.event_loop_thread.loop.call_soon_threadsafe(
                    future.set_exception, e
                )

        asyncio.run_coroutine_threadsafe(wrapped(), self.event_loop_thread.loop)
        return asyncio.wrap_future(future)

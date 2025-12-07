from python.helpers.extension import Extension
from agent import LoopData
from python.extensions.message_loop_end._10_organize_history import DATA_NAME_TASK
import asyncio


class OrganizeHistoryWait(Extension):
    """
    An extension that waits for the history compression task to complete if the
    history size is over the limit. This ensures the context window is not
    exceeded before generating the next prompt.
    """
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        """
        Executes the history organization wait extension.

        This method checks if the agent's history is over the token limit.
        If it is, it waits for any running compression task to finish. If no
        task is running, it triggers a new compression and waits for it.
        This process repeats until the history is within the limit.

        Args:
            loop_data: The current loop data.
            **kwargs: Arbitrary keyword arguments.
        """

        # sync action only required if the history is too large, otherwise leave it in background
        while self.agent.history.is_over_limit():
            # get task
            task = self.agent.get_data(DATA_NAME_TASK)

            # Check if the task is already done
            if task:
                if not task.done():
                    self.agent.context.log.set_progress("Compressing history...")

                # Wait for the task to complete
                await task

                # Clear the coroutine data after it's done
                self.agent.set_data(DATA_NAME_TASK, None)
            else:
                # no task running, start and wait
                self.agent.context.log.set_progress("Compressing history...")
                await self.agent.history.compress()


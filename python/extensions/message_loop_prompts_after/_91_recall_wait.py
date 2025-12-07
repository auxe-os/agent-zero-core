from python.helpers.extension import Extension
from agent import LoopData
from python.extensions.message_loop_prompts_after._50_recall_memories import DATA_NAME_TASK as DATA_NAME_TASK_MEMORIES, DATA_NAME_ITER as DATA_NAME_ITER_MEMORIES
# from python.extensions.message_loop_prompts_after._51_recall_solutions import DATA_NAME_TASK as DATA_NAME_TASK_SOLUTIONS
from python.helpers import settings

class RecallWait(Extension):
    """
    An extension that handles the waiting for asynchronous memory recall tasks.
    It can operate in two modes: either awaiting the task immediately or
    allowing it to run in the background and adding a note to the prompt.
    """
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        """
        Executes the recall wait extension.

        This method checks for a running memory recall task. If one exists,
        it either awaits its completion or, if in delayed mode, adds a message
        to the prompt indicating that memories are being recalled in the
        background.

        Args:
            loop_data: The current loop data.
            **kwargs: Arbitrary keyword arguments.
        """

        set = settings.get_settings()

        task = self.agent.get_data(DATA_NAME_TASK_MEMORIES)
        iter = self.agent.get_data(DATA_NAME_ITER_MEMORIES) or 0

        if task and not task.done():

            # if memory recall is set to delayed mode, do not await on the iteration it was called
            if set["memory_recall_delayed"]:
                if iter == loop_data.iteration:
                    # insert info about delayed memory to extras
                    delay_text = self.agent.read_prompt("memory.recall_delay_msg.md")
                    loop_data.extras_temporary["memory_recall_delayed"] = delay_text
                    return
            
            # otherwise await the task
            await task

        # task = self.agent.get_data(DATA_NAME_TASK_SOLUTIONS)
        # if task and not task.done():
        #     # self.agent.context.log.set_progress("Recalling solutions...")
        #     await task


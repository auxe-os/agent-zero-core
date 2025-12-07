import asyncio
from python.helpers.extension import Extension
from agent import LoopData

DATA_NAME_TASK = "_organize_history_task"


class OrganizeHistory(Extension):
    """
    An extension that triggers the history compression process at the end of a
    message loop. This is done asynchronously to avoid blocking the agent.
    """
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        """
        Executes the history organization extension.

        This method checks if a history compression task is already running.
        If not, it creates a new asynchronous task to compress the agent's
        history and stores it in the agent's data.

        Args:
            loop_data: The current loop data.
            **kwargs: Arbitrary keyword arguments.
        """
        # is there a running task? if yes, skip this round, the wait extension will double check the context size
        task = self.agent.get_data(DATA_NAME_TASK)
        if task and not task.done():
            return

        # start task
        task = asyncio.create_task(self.agent.history.compress())
        # set to agent to be able to wait for it
        self.agent.set_data(DATA_NAME_TASK, task)

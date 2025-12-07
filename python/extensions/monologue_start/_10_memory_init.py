from python.helpers.extension import Extension
from agent import LoopData
from python.helpers import memory
import asyncio


class MemoryInit(Extension):
    """
    An extension that initializes the memory database for the agent at the
    start of a monologue.
    """

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        """
        Executes the memory initialization extension.

        This method ensures that the memory database is initialized and ready
        for use by the agent.

        Args:
            loop_data: The current loop data.
            **kwargs: Arbitrary keyword arguments.
        """
        db = await memory.Memory.get(self.agent)
        

   
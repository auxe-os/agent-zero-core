from python.helpers.extension import Extension
from agent import Agent, LoopData

DATA_NAME_ITER_NO = "iteration_no"

class IterationNo(Extension):
    """
    An extension that tracks the total number of message loop iterations within
    an agent's session.
    """
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        """
        Executes the iteration counter extension.

        This method increments the iteration number stored in the agent's data
        at the start of each message loop.

        Args:
            loop_data: The current loop data.
            **kwargs: Arbitrary keyword arguments.
        """
        # total iteration number
        no = self.agent.get_data(DATA_NAME_ITER_NO) or 0
        self.agent.set_data(DATA_NAME_ITER_NO, no + 1)


def get_iter_no(agent: Agent) -> int:
    """
    Gets the current iteration number for a given agent.

    Args:
        agent: The agent instance.

    Returns:
        The current iteration number, or 0 if it has not been initialized.
    """
    return agent.get_data(DATA_NAME_ITER_NO) or 0
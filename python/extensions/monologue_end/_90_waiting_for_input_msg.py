from python.helpers.extension import Extension
from agent import LoopData

class WaitingForInputMsg(Extension):
    """
    An extension that displays a "Waiting for user input..." message in the UI
    at the end of the main agent's monologue.
    """

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        """
        Executes the extension to show the waiting message.

        This method checks if the agent is the main agent (agent number 0)
        and, if so, sets the initial progress message in the log.

        Args:
            loop_data: The current loop data.
            **kwargs: Arbitrary keyword arguments.
        """
        # show temp info message
        if self.agent.number == 0:
            self.agent.context.log.set_initial_progress()


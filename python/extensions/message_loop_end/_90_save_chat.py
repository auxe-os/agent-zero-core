from python.helpers.extension import Extension
from agent import LoopData, AgentContextType
from python.helpers import persist_chat


class SaveChat(Extension):
    """
    An extension that saves the current chat history to a temporary file at the
    end of a message loop. This provides a snapshot of the conversation for
    persistence and recovery.
    """
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        """
        Executes the chat saving extension.

        This method saves the agent's current context (including history) to a
        temporary file, unless the context is of type BACKGROUND.

        Args:
            loop_data: The current loop data.
            **kwargs: Arbitrary keyword arguments.
        """
        # Skip saving BACKGROUND contexts as they should be ephemeral
        if self.agent.context.type == AgentContextType.BACKGROUND:
            return

        persist_chat.save_tmp_chat(self.agent.context)

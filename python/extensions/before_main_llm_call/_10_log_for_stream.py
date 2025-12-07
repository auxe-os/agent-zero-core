from python.helpers import persist_chat, tokens
from python.helpers.extension import Extension
from agent import LoopData
import asyncio
from python.helpers.log import LogItem
from python.helpers import log
import math


class LogForStream(Extension):
    """
    An extension that creates a log item to display the "Generating..." status
    in the UI before the main LLM call is made for streaming responses.
    """

    async def execute(self, loop_data: LoopData = LoopData(), text: str = "", **kwargs):
        """
        Executes the extension to create the 'Generating...' log item.

        This method checks if a 'log_item_generating' already exists in the
        temporary parameters of the loop data. If not, it creates a new log
        item and stores it.

        Args:
            loop_data: The current loop data.
            text: Optional text (not used).
            **kwargs: Arbitrary keyword arguments.
        """
        # create log message and store it in loop data temporary params
        if "log_item_generating" not in loop_data.params_temporary:
            loop_data.params_temporary["log_item_generating"] = (
                self.agent.context.log.log(
                    type="agent",
                    heading=build_default_heading(self.agent),
                )
            )

def build_heading(agent, text: str):
    """
    Builds a standardized heading for log messages.

    Args:
        agent: The agent instance.
        text: The text to include in the heading.

    Returns:
        A formatted heading string.
    """
    return f"icon://network_intelligence {agent.agent_name}: {text}"

def build_default_heading(agent):
    """
    Builds the default "Generating..." heading for log messages.

    Args:
        agent: The agent instance.

    Returns:
        A formatted heading string with the text "Generating...".
    """
    return build_heading(agent, "Generating...") 
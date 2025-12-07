from python.helpers import persist_chat, tokens
from python.helpers.extension import Extension
from agent import LoopData
import asyncio
from python.helpers.log import LogItem
from python.helpers import log
import math
from python.extensions.before_main_llm_call._10_log_for_stream import build_heading, build_default_heading

class LogFromStream(Extension):
    """
    An extension that logs the agent's reasoning process as it streams from the LLM.
    It creates or updates a log item to display the in-progress reasoning.
    """

    async def execute(self, loop_data: LoopData = LoopData(), text: str = "", **kwargs):
        """
        Executes the reasoning stream logging extension.

        This method updates the heading of the "Generating..." log item with a
        visual indicator of the reasoning text's length and streams the
        reasoning text to the log.

        Args:
            loop_data: The current loop data, containing the log item.
            text: The chunk of reasoning text that has been streamed.
            **kwargs: Arbitrary keyword arguments.
        """

        # thought length indicator
        pipes = "|" * math.ceil(math.sqrt(len(text)))
        heading = build_heading(self.agent, f"Reasoning.. {pipes}")

        # create log message and store it in loop data temporary params
        if "log_item_generating" not in loop_data.params_temporary:
            loop_data.params_temporary["log_item_generating"] = (
                self.agent.context.log.log(
                    type="agent",
                    heading=heading,
                )
            )

        # update log message
        log_item = loop_data.params_temporary["log_item_generating"]
        log_item.update(heading=heading, reasoning=text)

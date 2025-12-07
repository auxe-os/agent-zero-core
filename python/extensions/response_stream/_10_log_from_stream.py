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
    An extension that logs the agent's response as it is being streamed from the LLM.
    It intelligently updates the log heading based on the content of the stream.
    """

    async def execute(
        self,
        loop_data: LoopData = LoopData(),
        text: str = "",
        parsed: dict = {},
        **kwargs,
    ):
        """
        Executes the response stream logging extension.

        This method creates or updates a log item for the agent's response.
        The heading is dynamically updated to reflect the agent's current action,
        such as thinking, using a tool, or providing a headline.

        Args:
            loop_data: The current loop data.
            text: The full response text streamed so far.
            parsed: A dictionary of parsed components from the stream (e.g.,
                      thoughts, tool_name, headline).
            **kwargs: Arbitrary keyword arguments.
        """

        heading = build_default_heading(self.agent)
        if "headline" in parsed:
            heading = build_heading(self.agent, parsed['headline'])
        elif "tool_name" in parsed:
            heading = build_heading(self.agent, f"Using tool {parsed['tool_name']}") # if the llm skipped headline
        elif "thoughts" in parsed:
            # thought length indicator
            thoughts = "\n".join(parsed["thoughts"])
            pipes = "|" * math.ceil(math.sqrt(len(thoughts)))
            heading = build_heading(self.agent, f"Thinking... {pipes}")
        
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

        # keep reasoning from previous logs in kvps
        kvps = {}
        if log_item.kvps is not None and "reasoning" in log_item.kvps:
            kvps["reasoning"] = log_item.kvps["reasoning"]
        kvps.update(parsed)

        # update the log item
        log_item.update(heading=heading, content=text, kvps=kvps)
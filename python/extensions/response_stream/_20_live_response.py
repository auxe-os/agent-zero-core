from python.helpers import persist_chat, tokens
from python.helpers.extension import Extension
from agent import LoopData
import asyncio
from python.helpers.log import LogItem
from python.helpers import log


class LiveResponse(Extension):
    """
    An extension that handles the live streaming of the agent's final response
    to the user interface.
    """

    async def execute(
        self,
        loop_data: LoopData = LoopData(),
        text: str = "",
        parsed: dict = {},
        **kwargs,
    ):
        """
        Executes the live response extension.

        This method checks if the streamed tool call is a 'response' tool. If it
        is, it creates or updates a 'response' type log item to display the
        streaming text to the user in real-time.

        Args:
            loop_data: The current loop data.
            text: The full response text streamed so far.
            parsed: A dictionary of parsed components from the stream.
            **kwargs: Arbitrary keyword arguments.
        """
        try:
            if (
                not "tool_name" in parsed
                or parsed["tool_name"] != "response"
                or "tool_args" not in parsed
                or "text" not in parsed["tool_args"]
                or not parsed["tool_args"]["text"]
            ):
                return  # not a response

            # create log message and store it in loop data temporary params
            if "log_item_response" not in loop_data.params_temporary:
                loop_data.params_temporary["log_item_response"] = (
                    self.agent.context.log.log(
                        type="response",
                        heading=f"icon://chat {self.agent.agent_name}: Responding",
                    )
                )

            # update log message
            log_item = loop_data.params_temporary["log_item_response"]
            log_item.update(content=parsed["tool_args"]["text"])
        except Exception as e:
            pass

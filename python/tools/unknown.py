from python.helpers.tool import Tool, Response
from python.extensions.system_prompt._10_system_prompt import (
    get_tools_prompt,
)


class Unknown(Tool):
    """
    A tool that is executed when the agent tries to use a tool that doesn't exist.
    It provides a helpful error message to the agent, listing the available tools.
    """
    async def execute(self, **kwargs):
        """
        Executes the unknown tool handler.

        This method informs the agent that the tool it tried to use was not
        found and provides a list of available tools to help it correct its mistake.

        Args:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            A Response object containing the error message.
        """
        tools = get_tools_prompt(self.agent)
        return Response(
            message=self.agent.read_prompt(
                "fw.tool_not_found.md", tool_name=self.name, tools_prompt=tools
            ),
            break_loop=False,
        )

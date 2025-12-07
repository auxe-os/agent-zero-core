from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from agent import Agent, LoopData
from python.helpers.print_style import PrintStyle
from python.helpers.strings import sanitize_string


@dataclass
class Response:
    """Represents the response from a tool.

    Attributes:
        message: The message to be returned to the agent.
        break_loop: Whether to break the agent's message loop.
        additional: A dictionary of additional data to be added to the
                    tool result in the history.
    """
    message:str
    break_loop: bool
    additional: dict[str, Any] | None = None

class Tool:
    """An abstract base class for tools."""

    def __init__(self, agent: Agent, name: str, method: str | None, args: dict[str,str], message: str, loop_data: LoopData | None, **kwargs) -> None:
        """Initializes a Tool.

        Args:
            agent: The agent that is using the tool.
            name: The name of the tool.
            method: The method of the tool to be called.
            args: The arguments for the tool.
            message: The message that triggered the tool.
            loop_data: The data for the current message loop iteration.
            **kwargs: Additional keyword arguments.
        """
        self.agent = agent
        self.name = name
        self.method = method
        self.args = args
        self.loop_data = loop_data
        self.message = message
        self.progress: str = ""

    @abstractmethod
    async def execute(self,**kwargs) -> Response:
        """Executes the tool.

        This method must be implemented by subclasses.

        Args:
            **kwargs: The arguments for the tool.

        Returns:
            A Response object.
        """
        pass

    def set_progress(self, content: str | None):
        """Sets the progress of the tool.

        Args:
            content: The progress content.
        """
        self.progress = content or ""

    def add_progress(self, content: str | None):
        """Adds to the progress of the tool.

        Args:
            content: The progress content to add.
        """
        if not content:
            return
        self.progress += content

    async def before_execution(self, **kwargs):
        """Called before the tool is executed."""
        PrintStyle(font_color="#1B4F72", padding=True, background_color="white", bold=True).print(f"{self.agent.agent_name}: Using tool '{self.name}'")
        self.log = self.get_log_object()
        if self.args and isinstance(self.args, dict):
            for key, value in self.args.items():
                PrintStyle(font_color="#85C1E9", bold=True).stream(self.nice_key(key)+": ")
                PrintStyle(font_color="#85C1E9", padding=isinstance(value,str) and "\n" in value).stream(value)
                PrintStyle().print()

    async def after_execution(self, response: Response, **kwargs):
        """Called after the tool is executed.

        Args:
            response: The response from the tool.
        """
        text = sanitize_string(response.message.strip())
        self.agent.hist_add_tool_result(self.name, text, **(response.additional or {}))
        PrintStyle(font_color="#1B4F72", background_color="white", padding=True, bold=True).print(f"{self.agent.agent_name}: Response from tool '{self.name}'")
        PrintStyle(font_color="#85C1E9").print(text)
        self.log.update(content=text)

    def get_log_object(self):
        """Gets the log object for the tool."""
        if self.method:
            heading = f"icon://construction {self.agent.agent_name}: Using tool '{self.name}:{self.method}'"
        else:
            heading = f"icon://construction {self.agent.agent_name}: Using tool '{self.name}'"
        return self.agent.context.log.log(type="tool", heading=heading, content="", kvps=self.args)

    def nice_key(self, key:str):
        """Converts a snake_case key to a nice-looking string."""
        words = key.split('_')
        words = [words[0].capitalize()] + [word.lower() for word in words[1:]]
        result = ' '.join(words)
        return result

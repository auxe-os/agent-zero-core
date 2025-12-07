from agent import Agent, UserMessage
from python.helpers.tool import Tool, Response
from python.tools.code_execution_tool import CodeExecution


class Input(Tool):
    """
    A tool to simulate keyboard input by forwarding it to the code execution tool.
    This is useful for interacting with running processes in a terminal session.
    """

    async def execute(self, keyboard="", **kwargs):
        """
        Executes the keyboard input tool.

        Args:
            keyboard: The string of keyboard input to be sent to the terminal.
            **kwargs: Arbitrary keyword arguments, including 'session' for the
                      terminal session number.

        Returns:
            The Response object from the code execution tool.
        """
        # normalize keyboard input
        keyboard = keyboard.rstrip()
        # keyboard += "\n" # no need to, code_exec does that
        
        # terminal session number
        session = int(self.args.get("session", 0))

        # forward keyboard input to code execution tool
        args = {"runtime": "terminal", "code": keyboard, "session": session, "allow_running": True}
        cet = CodeExecution(self.agent, "code_execution_tool", "", args, self.message, self.loop_data)
        cet.log = self.log
        return await cet.execute(**args)

    def get_log_object(self):
        """
        Creates a log object for the keyboard input event.

        Returns:
            A log object with a keyboard icon and relevant details.
        """
        return self.agent.context.log.log(type="code_exe", heading=f"icon://keyboard {self.agent.agent_name}: Using tool '{self.name}'", content="", kvps=self.args)

    async def after_execution(self, response, **kwargs):
        """
        Adds the tool's result to the agent's history after execution.

        Args:
            response: The Response object from the execution.
            **kwargs: Arbitrary keyword arguments.
        """
        self.agent.hist_add_tool_result(self.name, response.message, **(response.additional or {}))
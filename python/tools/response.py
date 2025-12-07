from python.helpers.tool import Tool, Response


class ResponseTool(Tool):
    """
    A tool for providing the final response from the agent and breaking the
    execution loop.
    """

    async def execute(self, **kwargs):
        """
        Executes the response tool.

        This method returns a Response object with the final message and sets
        the `break_loop` flag to True, signaling the end of the agent's turn.

        Args:
            **kwargs: Arbitrary keyword arguments, expected to contain 'text' or
                      'message'.

        Returns:
            A Response object with the final message and `break_loop=True`.
        """
        return Response(message=self.args["text"] if "text" in self.args else self.args["message"], break_loop=True)

    async def before_execution(self, **kwargs):
        """
        Hook that runs before the tool's execution. Currently does nothing.
        """
        # self.log = self.agent.context.log.log(type="response", heading=f"{self.agent.agent_name}: Responding", content=self.args.get("text", ""))
        # don't log here anymore, we have the live_response extension now
        pass

    async def after_execution(self, response, **kwargs):
        """
        Hook that runs after the tool's execution.

        This method marks the live response log item as finished.
        """
        # do not add anything to the history or output

        if self.loop_data and "log_item_response" in self.loop_data.params_temporary:
            log = self.loop_data.params_temporary["log_item_response"]
            log.update(finished=True) # mark the message as finished

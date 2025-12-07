from python.helpers.extension import Extension
from python.helpers.secrets import get_secrets_manager
from python.helpers.tool import Response


class MaskToolSecrets(Extension):
    """
    An extension that masks sensitive information in the response message from a
    tool execution.
    """

    async def execute(self, response: Response | None = None, **kwargs):
        """
        Executes the tool secret masking extension.

        This method takes the response object from a tool, and if it exists,
        it masks any secrets found in the response message.

        Args:
            response: The Response object from the tool execution.
            **kwargs: Arbitrary keyword arguments.
        """
        if not response:
            return
        secrets_mgr = get_secrets_manager(self.agent.context)
        response.message = secrets_mgr.mask_values(response.message)

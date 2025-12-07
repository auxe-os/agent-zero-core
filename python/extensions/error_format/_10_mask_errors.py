from python.helpers.extension import Extension
from python.helpers.secrets import get_secrets_manager


class MaskErrorSecrets(Extension):
    """
    An extension that masks sensitive information (secrets) in error messages
    before they are logged or displayed.
    """

    async def execute(self, **kwargs):
        """
        Executes the error masking extension.

        This method retrieves the error message from the keyword arguments and uses
        the secrets manager to mask any sensitive values within the message.

        Args:
            **kwargs: Arbitrary keyword arguments. Expected to contain 'msg',
                      which is a dictionary with a 'message' key.
        """
        # Get error data from kwargs
        msg = kwargs.get("msg")
        if not msg:
            return

        secrets_mgr = get_secrets_manager(self.agent.context)

        # Mask the error message
        if "message" in msg:
            msg["message"] = secrets_mgr.mask_values(msg["message"])

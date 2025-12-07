from python.helpers.extension import Extension
from python.helpers.secrets import get_secrets_manager


class UnmaskToolSecrets(Extension):
    """
    An extension that unmasks secrets in tool arguments before the tool is
    executed. It replaces secret placeholders with their actual values.
    """

    async def execute(self, **kwargs):
        """
        Executes the tool secret unmasking extension.

        This method iterates through the tool's arguments and replaces any
        secret placeholders (e.g., {{my_secret}}) with their actual values from
        the secrets manager.

        Args:
            **kwargs: Arbitrary keyword arguments. Expected to contain 'tool_args'.
        """
        # Get tool args from kwargs
        tool_args = kwargs.get("tool_args")
        if not tool_args:
            return

        secrets_mgr = get_secrets_manager(self.agent.context)

        # Unmask placeholders in args for actual tool execution
        for k, v in tool_args.items():
            if isinstance(v, str):
                tool_args[k] = secrets_mgr.replace_placeholders(v)

from python.helpers.extension import Extension
from python.helpers.secrets import get_secrets_manager


class MaskHistoryContent(Extension):
    """
    An extension that masks sensitive information in the content of messages
    before they are added to the agent's history.
    """

    async def execute(self, **kwargs):
        """
        Executes the history content masking extension.

        This method retrieves the message content from the keyword arguments and
        recursively masks any sensitive values within it.

        Args:
            **kwargs: Arbitrary keyword arguments. Expected to contain
                      'content_data', a dictionary with a 'content' key.
        """
        # Get content data from kwargs
        content_data = kwargs.get("content_data")
        if not content_data:
            return

        try:
            secrets_mgr = get_secrets_manager(self.agent.context)

            # Mask the content before adding to history
            content_data["content"] = self._mask_content(content_data["content"], secrets_mgr)
        except Exception as e:
            # If masking fails, proceed without masking
            pass

    def _mask_content(self, content, secrets_mgr):
        """
        Recursively masks secrets in message content.

        This function handles strings, lists, and dictionaries, traversing them
        to find and mask sensitive values.

        Args:
            content: The content to be masked (can be str, list, or dict).
            secrets_mgr: The secrets manager instance.

        Returns:
            The content with any sensitive information masked.
        """
        if isinstance(content, str):
            return secrets_mgr.mask_values(content)
        elif isinstance(content, list):
            return [self._mask_content(item, secrets_mgr) for item in content]
        elif isinstance(content, dict):
            return {k: self._mask_content(v, secrets_mgr) for k, v in content.items()}
        else:
            # For other types, return as-is
            return content

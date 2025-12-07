from typing import Any
from python.helpers.extension import Extension


class ReplaceLastToolOutput(Extension):
    """
    An extension that replaces placeholders like {last_tool_output} in a tool's
    arguments with the actual output from the previously executed tool.
    """
    async def execute(self, tool_args: dict[str, Any] | None = None, tool_name: str = "", **kwargs):
        """
        Executes the placeholder replacement extension.

        This method recursively searches through the arguments of the current
        tool call and replaces any instances of '{last_tool_output}' with the
        output of the last tool call.

        Args:
            tool_args: The arguments for the tool about to be executed.
            tool_name: The name of the tool about to be executed.
            **kwargs: Arbitrary keyword arguments.
        """
        if not tool_args:
            return

        last_call = self.agent.get_data("last_tool_call") or {}
        last_output = last_call.get("last_tool_output", "")
        if not last_output:
            return

        tokens = ("{last_tool_output}", "{{last_tool_output}}")

        def replace_placeholders(value: Any) -> Any:
            if isinstance(value, str):
                new_val = value
                for token in tokens:
                    new_val = new_val.replace(token, last_output)
                return new_val
            if isinstance(value, dict):
                return {k: replace_placeholders(v) for k, v in value.items()}
            if isinstance(value, list):
                return [replace_placeholders(v) for v in value]
            if isinstance(value, tuple):
                return tuple(replace_placeholders(v) for v in value)
            return value

        updated_args = replace_placeholders(tool_args)
        tool_args.clear()
        tool_args.update(updated_args)

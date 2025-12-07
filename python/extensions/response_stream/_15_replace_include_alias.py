from typing import Any
from python.helpers.extension import Extension
from python.helpers.strings import replace_file_includes


class ReplaceIncludeAlias(Extension):
    """
    An extension that replaces file inclusion aliases (e.g., §§include(path/to/file))
    with the actual file content within the arguments of a tool call.
    """
    async def execute(
        self,
        loop_data=None,
        text: str = "",
        parsed: dict[str, Any] | None = None,
        **kwargs
    ):
        """
        Executes the include alias replacement extension.

        This method recursively traverses the 'tool_args' in the parsed stream
        data and replaces any file inclusion aliases with the content of the
        specified files.

        Args:
            loop_data: The current loop data.
            text: The full response text streamed so far.
            parsed: A dictionary of parsed components from the stream, which may
                      contain 'tool_name' and 'tool_args'.
            **kwargs: Arbitrary keyword arguments.
        """
        if not parsed or not isinstance(parsed, dict):
            return

        def replace_placeholders(value: Any) -> Any:
            if isinstance(value, str):
                new_val = value
                new_val = replace_file_includes(new_val, r"§§include\(([^)]+)\)")
                return new_val
            if isinstance(value, dict):
                return {k: replace_placeholders(v) for k, v in value.items()}
            if isinstance(value, list):
                return [replace_placeholders(v) for v in value]
            if isinstance(value, tuple):
                return tuple(replace_placeholders(v) for v in value)
            return value

        if "tool_args" in parsed and "tool_name" in parsed:
            parsed["tool_args"] = replace_placeholders(parsed["tool_args"])

from typing import Any
from python.helpers.extension import Extension
from python.helpers import files, persist_chat
import os, re

LEN_MIN = 500

class SaveToolCallFile(Extension):
    """
    An extension that saves the result of a tool call to a file if the result is
    sufficiently long. This is useful for keeping the main history concise while
_   preserving large outputs for later inspection.
    """
    async def execute(self, data: dict[str, Any] | None = None, **kwargs):
        """
        Executes the extension to save the tool call result.

        This method checks the length of the tool result. If it exceeds a
        minimum threshold, the result is written to a new text file in the
        chat's message files directory. The path to this new file is then
        added to the history data.

        Args:
            data: A dictionary containing the tool call data, including the
                  'tool_result'.
            **kwargs: Arbitrary keyword arguments.
        """
        if not data:
            return

        # get tool call result
        result = data.get("tool_result") if isinstance(data, dict) else None
        if result is None:
            return

        # skip short results
        if len(str(result)) < LEN_MIN:
            return

        # message files directory
        msgs_folder = persist_chat.get_chat_msg_files_folder(self.agent.context.id)
        os.makedirs(msgs_folder, exist_ok=True)

        # count the files in the directory
        last_num = len(os.listdir(msgs_folder))

        # create new file
        new_file = files.get_abs_path(msgs_folder, f"{last_num+1}.txt")
        files.write_file(
            new_file,
            result,
        )

        # add the path to the history
        data["file"] = new_file

from python.helpers import persist_chat, tokens
from python.helpers.extension import Extension
from agent import LoopData
import asyncio


class RenameChat(Extension):
    """
    An extension that automatically renames the chat session based on the
    conversation history. This is done asynchronously in the background.
    """

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        """
        Executes the chat renaming extension.

        This method creates an asynchronous task to handle the renaming process,
        allowing the agent to continue its main tasks without delay.

        Args:
            loop_data: The current loop data.
            **kwargs: Arbitrary keyword arguments.
        """
        asyncio.create_task(self.change_name())

    async def change_name(self):
        """
        Performs the actual chat renaming process.

        It summarizes the conversation history, calls a utility model to generate
        a suitable new name, and then updates the chat context with the new name.
        """
        try:
            # prepare history
            history_text = self.agent.history.output_text()
            ctx_length = min(
                int(self.agent.config.utility_model.ctx_length * 0.7), 5000
            )
            history_text = tokens.trim_to_tokens(history_text, ctx_length, "start")
            # prepare system and user prompt
            system = self.agent.read_prompt("fw.rename_chat.sys.md")
            current_name = self.agent.context.name
            message = self.agent.read_prompt(
                "fw.rename_chat.msg.md", current_name=current_name, history=history_text
            )
            # call utility model
            new_name = await self.agent.call_utility_model(
                system=system, message=message, background=True
            )
            # update name
            if new_name:
                # trim name to max length if needed
                if len(new_name) > 40:
                    new_name = new_name[:40] + "..."
                # apply to context and save
                self.agent.context.name = new_name
                persist_chat.save_tmp_chat(self.agent.context)
        except Exception as e:
            pass  # non-critical

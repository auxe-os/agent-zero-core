from python.helpers.memory import Memory
from python.helpers.tool import Tool, Response


class MemorySave(Tool):
    """
    A tool for saving text as a memory (document) in the vector database.
    """

    async def execute(self, text="", area="", **kwargs):
        """
        Executes the memory saving tool.

        This method takes a string of text and saves it as a document in the
        vector database, along with any provided metadata.

        Args:
            text: The text content of the memory to save.
            area: The memory area to save the document to (e.g., 'main', 'scratchpad').
            **kwargs: Arbitrary keyword arguments to be stored as metadata.

        Returns:
            A Response object with a message indicating that the memory has
            been saved, including its new ID.
        """

        if not area:
            area = Memory.Area.MAIN.value

        metadata = {"area": area, **kwargs}

        db = await Memory.get(self.agent)
        id = await db.insert_text(text, metadata)

        result = self.agent.read_prompt("fw.memory_saved.md", memory_id=id)
        return Response(message=result, break_loop=False)

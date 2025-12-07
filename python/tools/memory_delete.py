from python.helpers.memory import Memory
from python.helpers.tool import Tool, Response


class MemoryDelete(Tool):
    """
    A tool for deleting memories (documents) from the vector database by their IDs.
    """

    async def execute(self, ids="", **kwargs):
        """
        Executes the memory deletion tool.

        Args:
            ids: A comma-separated string of document IDs to be deleted.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            A Response object with a message indicating the number of memories
            that were deleted.
        """
        db = await Memory.get(self.agent)
        ids = [id.strip() for id in ids.split(",") if id.strip()]
        dels = await db.delete_documents_by_ids(ids=ids)

        result = self.agent.read_prompt("fw.memories_deleted.md", memory_count=len(dels))
        return Response(message=result, break_loop=False)

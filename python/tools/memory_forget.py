from python.helpers.memory import Memory
from python.helpers.tool import Tool, Response
from python.tools.memory_load import DEFAULT_THRESHOLD


class MemoryForget(Tool):
    """
    A tool for forgetting memories (documents) from the vector database that
    match a specific query.
    """

    async def execute(self, query="", threshold=DEFAULT_THRESHOLD, filter="", **kwargs):
        """
        Executes the memory forgetting tool.

        This method finds documents similar to the given query and deletes them.

        Args:
            query: The query to find matching memories to forget.
            threshold: The similarity threshold for matching documents.
            filter: An optional filter to apply to the search.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            A Response object with a message indicating the number of memories
            that were forgotten.
        """
        db = await Memory.get(self.agent)
        dels = await db.delete_documents_by_query(query=query, threshold=threshold, filter=filter)

        result = self.agent.read_prompt("fw.memories_deleted.md", memory_count=len(dels))
        return Response(message=result, break_loop=False)

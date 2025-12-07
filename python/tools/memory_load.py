from python.helpers.memory import Memory
from python.helpers.tool import Tool, Response

DEFAULT_THRESHOLD = 0.7
DEFAULT_LIMIT = 10


class MemoryLoad(Tool):
    """
    A tool for loading memories (documents) from the vector database that are
    similar to a given query.
    """

    async def execute(self, query="", threshold=DEFAULT_THRESHOLD, limit=DEFAULT_LIMIT, filter="", **kwargs):
        """
        Executes the memory loading tool.

        This method searches for documents in the vector database that are
        similar to the provided query and above a certain similarity threshold.

        Args:
            query: The query to search for similar memories.
            threshold: The similarity threshold for matching documents.
            limit: The maximum number of documents to return.
            filter: An optional filter to apply to the search.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            A Response object containing the formatted content of the found
            memories, or a message indicating that no memories were found.
        """
        db = await Memory.get(self.agent)
        docs = await db.search_similarity_threshold(query=query, limit=limit, threshold=threshold, filter=filter)

        if len(docs) == 0:
            result = self.agent.read_prompt("fw.memories_not_found.md", query=query)
        else:
            text = "\n\n".join(Memory.format_docs_plain(docs))
            result = str(text)

        return Response(message=result, break_loop=False)

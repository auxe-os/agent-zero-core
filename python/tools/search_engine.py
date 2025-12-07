from python.helpers.tool import Tool, Response
from python.helpers.errors import handle_error
from python.helpers.searxng import search as searxng

SEARCH_ENGINE_RESULTS = 10


class SearchEngine(Tool):
    """
    A tool for performing web searches using the SearXNG meta-search engine.
    """
    async def execute(self, query="", **kwargs):
        """
        Executes the search engine tool.

        Args:
            query: The search query string.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            A Response object containing the formatted search results.
        """

        searxng_result = await self.searxng_search(query)

        await self.agent.handle_intervention(
            searxng_result
        )  # wait for intervention and handle it, if paused

        return Response(message=searxng_result, break_loop=False)


    async def searxng_search(self, question):
        """
        Performs a search using SearXNG and formats the results.

        Args:
            question: The search query.

        Returns:
            A formatted string of the search results.
        """
        results = await searxng(question)
        return self.format_result_searxng(results, "Search Engine")

    def format_result_searxng(self, result, source):
        """
        Formats the raw search results from SearXNG into a readable string.

        Args:
            result: The dictionary of search results from SearXNG.
            source: The name of the search source (e.g., "Search Engine").

        Returns:
            A formatted string of the search results, or an error message if
            the search failed.
        """
        if isinstance(result, Exception):
            handle_error(result)
            return f"{source} search failed: {str(result)}"

        outputs = []
        for item in result["results"]:
            outputs.append(f"{item['title']}\n{item['url']}\n{item['content']}")

        return "\n\n".join(outputs[:SEARCH_ENGINE_RESULTS]).strip()

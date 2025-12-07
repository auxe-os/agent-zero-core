import asyncio

from python.helpers.tool import Tool, Response
from python.helpers.document_query import DocumentQueryHelper


class DocumentQueryTool(Tool):
    """
    A tool for querying documents. It can retrieve the full content of documents
    or perform question-answering on them if queries are provided.
    """

    async def execute(self, **kwargs):
        """
        Executes the document query tool.

        This method handles both retrieving full document content and performing
        question-answering based on the provided arguments.

        Args:
            **kwargs: Arbitrary keyword arguments. Expected keys are 'document'
                      (or 'documents') and optionally 'query' (or 'queries').

        Returns:
            A Response object containing the document content or the answer
            to the query, or an error message.
        """
        document_uri = kwargs.get("document")
        document_uris = []

        if isinstance(document_uri, list):
            document_uris = document_uri
        elif isinstance(document_uri, str):
            document_uris = [document_uri]

        if not document_uris:
            return Response(message="Error: no document provided", break_loop=False)

        queries = (
            kwargs["queries"]
            if "queries" in kwargs
            else [kwargs["query"]]
            if ("query" in kwargs and kwargs["query"])
            else []
        )
        try:

            progress = []

            # logging callback
            def progress_callback(msg):
                progress.append(msg)
                self.log.update(progress="\n".join(progress))
            
            helper = DocumentQueryHelper(self.agent, progress_callback)
            if not queries:
                contents = await asyncio.gather(
                    *[helper.document_get_content(uri) for uri in document_uris]
                )
                content = "\n\n---\n\n".join(contents)
            else:
                _, content = await helper.document_qa(document_uris, queries)
            return Response(message=content, break_loop=False)
        except Exception as e:  # pylint: disable=broad-exception-caught
            return Response(message=f"Error processing document: {e}", break_loop=False)

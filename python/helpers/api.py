from abc import abstractmethod
import json
import threading
from typing import Union, TypedDict, Dict, Any
from attr import dataclass
from flask import Request, Response, jsonify, Flask, session, request, send_file
from agent import AgentContext
from initialize import initialize_agent
from python.helpers.print_style import PrintStyle
from python.helpers.errors import format_error
from werkzeug.serving import make_server

Input = dict
Output = Union[Dict[str, Any], Response, TypedDict]  # type: ignore


class ApiHandler:
    """An abstract base class for API handlers."""
    def __init__(self, app: Flask, thread_lock: threading.Lock):
        """Initializes an ApiHandler.

        Args:
            app: The Flask application.
            thread_lock: A lock for thread safety.
        """
        self.app = app
        self.thread_lock = thread_lock

    @classmethod
    def requires_loopback(cls) -> bool:
        """Whether the handler requires a loopback connection."""
        return False

    @classmethod
    def requires_api_key(cls) -> bool:
        """Whether the handler requires an API key."""
        return False

    @classmethod
    def requires_auth(cls) -> bool:
        """Whether the handler requires authentication."""
        return True

    @classmethod
    def get_methods(cls) -> list[str]:
        """Gets the HTTP methods that the handler supports."""
        return ["POST"]

    @classmethod
    def requires_csrf(cls) -> bool:
        """Whether the handler requires CSRF protection."""
        return cls.requires_auth()

    @abstractmethod
    async def process(self, input: Input, request: Request) -> Output:
        """Processes a request.

        This method must be implemented by subclasses.

        Args:
            input: The input data from the request.
            request: The Flask request object.

        Returns:
            The output to be sent in the response.
        """
        pass

    async def handle_request(self, request: Request) -> Response:
        """Handles a request.

        Args:
            request: The Flask request object.

        Returns:
            A Flask response object.
        """
        try:
            # input data from request based on type
            input_data: Input = {}
            if request.is_json:
                try:
                    if request.data:  # Check if there's any data
                        input_data = request.get_json()
                    # If empty or not valid JSON, use empty dict
                except Exception as e:
                    # Just log the error and continue with empty input
                    PrintStyle().print(f"Error parsing JSON: {str(e)}")
                    input_data = {}
            else:
                # input_data = {"data": request.get_data(as_text=True)}
                input_data = {}


            # process via handler
            output = await self.process(input_data, request)

            # return output based on type
            if isinstance(output, Response):
                return output
            else:
                response_json = json.dumps(output)
                return Response(
                    response=response_json, status=200, mimetype="application/json"
                )

            # return exceptions with 500
        except Exception as e:
            error = format_error(e)
            PrintStyle.error(f"API error: {error}")
            return Response(response=error, status=500, mimetype="text/plain")

    # get context to run agent zero in
    def use_context(self, ctxid: str, create_if_not_exists: bool = True):
        """Gets or creates an agent context.

        Args:
            ctxid: The ID of the context to use.
            create_if_not_exists: Whether to create the context if it does
                                  not exist.

        Returns:
            The agent context.
        """
        with self.thread_lock:
            if not ctxid:
                first = AgentContext.first()
                if first:
                    AgentContext.use(first.id)
                    return first
                context = AgentContext(config=initialize_agent(), set_current=True)
                return context
            got = AgentContext.use(ctxid)
            if got:
                return got
            if create_if_not_exists:
                context = AgentContext(config=initialize_agent(), id=ctxid, set_current=True)
                return context
            else:
                raise Exception(f"Context {ctxid} not found")
            

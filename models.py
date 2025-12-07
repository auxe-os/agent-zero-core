from dataclasses import dataclass, field
from enum import Enum
import logging
import os
from typing import (
    Any,
    Awaitable,
    Callable,
    List,
    Optional,
    Iterator,
    AsyncIterator,
    Tuple,
    TypedDict,
)

from litellm import completion, acompletion, embedding
import litellm
import openai
from litellm.types.utils import ModelResponse

from python.helpers import dotenv
from python.helpers import settings, dirty_json
from python.helpers.dotenv import load_dotenv
from python.helpers.providers import get_provider_config
from python.helpers.rate_limiter import RateLimiter
from python.helpers.tokens import approximate_tokens
from python.helpers import dirty_json, browser_use_monkeypatch

from langchain_core.language_models.chat_models import SimpleChatModel
from langchain_core.outputs.chat_generation import ChatGenerationChunk
from langchain_core.callbacks.manager import (
    CallbackManagerForLLMRun,
    AsyncCallbackManagerForLLMRun,
)
from langchain_core.messages import (
    BaseMessage,
    AIMessageChunk,
    HumanMessage,
    SystemMessage,
)
from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer
from pydantic import ConfigDict


# disable extra logging, must be done repeatedly, otherwise browser-use will turn it back on for some reason
def turn_off_logging():
    os.environ["LITELLM_LOG"] = "ERROR"  # only errors
    litellm.suppress_debug_info = True
    # Silence **all** LiteLLM sub-loggers (utils, cost_calculator…)
    for name in logging.Logger.manager.loggerDict:
        if name.lower().startswith("litellm"):
            logging.getLogger(name).setLevel(logging.ERROR)


# init
load_dotenv()
turn_off_logging()
browser_use_monkeypatch.apply()

litellm.modify_params = True # helps fix anthropic tool calls by browser-use

class ModelType(Enum):
    """Enumeration for the types of models."""
    CHAT = "Chat"
    EMBEDDING = "Embedding"


@dataclass
class ModelConfig:
    """Dataclass for configuring a model.

    Attributes:
        type: The type of the model (chat or embedding).
        provider: The provider of the model (e.g., 'openai', 'anthropic').
        name: The name of the model (e.g., 'gpt-4', 'claude-2').
        api_base: The base URL for the API.
        ctx_length: The context length of the model.
        limit_requests: The maximum number of requests per minute.
        limit_input: The maximum number of input tokens per minute.
        limit_output: The maximum number of output tokens per minute.
        vision: Whether the model has vision capabilities.
        kwargs: Additional keyword arguments for the model.
    """
    type: ModelType
    provider: str
    name: str
    api_base: str = ""
    ctx_length: int = 0
    limit_requests: int = 0
    limit_input: int = 0
    limit_output: int = 0
    vision: bool = False
    kwargs: dict = field(default_factory=dict)

    def build_kwargs(self):
        """Builds the keyword arguments for the model.

        Returns:
            A dictionary of keyword arguments.
        """
        kwargs = self.kwargs.copy() or {}
        if self.api_base and "api_base" not in kwargs:
            kwargs["api_base"] = self.api_base
        return kwargs


class ChatChunk(TypedDict):
    """Simplified response chunk for chat models."""
    response_delta: str
    reasoning_delta: str

class ChatGenerationResult:
    """Processes and accumulates chat generation chunks.

    This class handles the logic for parsing reasoning and response deltas,
    including the handling of "thinking" tags.
    """
    def __init__(self, chunk: ChatChunk|None = None):
        """Initializes the ChatGenerationResult.

        Args:
            chunk: An optional initial chunk to process.
        """
        self.reasoning = ""
        self.response = ""
        self.thinking = False
        self.thinking_tag = ""
        self.unprocessed = ""
        self.native_reasoning = False
        self.thinking_pairs = [("<think>", "</think>"), ("<reasoning>", "</reasoning>")]
        if chunk:
            self.add_chunk(chunk)

    def add_chunk(self, chunk: ChatChunk) -> ChatChunk:
        """Adds a chunk to the result.

        Args:
            chunk: The chunk to add.

        Returns:
            The processed chunk.
        """
        if chunk["reasoning_delta"]:
            self.native_reasoning = True

        # if native reasoning detection works, there's no need to worry about thinking tags
        if self.native_reasoning:
            processed_chunk = ChatChunk(response_delta=chunk["response_delta"], reasoning_delta=chunk["reasoning_delta"])
        else:
            # if the model outputs thinking tags, we ned to parse them manually as reasoning
            processed_chunk = self._process_thinking_chunk(chunk)

        self.reasoning += processed_chunk["reasoning_delta"]
        self.response += processed_chunk["response_delta"]

        return processed_chunk

    def _process_thinking_chunk(self, chunk: ChatChunk) -> ChatChunk:
        response_delta = self.unprocessed + chunk["response_delta"]
        self.unprocessed = ""
        return self._process_thinking_tags(response_delta, chunk["reasoning_delta"])

    def _process_thinking_tags(self, response: str, reasoning: str) -> ChatChunk:
        if self.thinking:
            close_pos = response.find(self.thinking_tag)
            if close_pos != -1:
                reasoning += response[:close_pos]
                response = response[close_pos + len(self.thinking_tag):]
                self.thinking = False
                self.thinking_tag = ""
            else:
                if self._is_partial_closing_tag(response):
                    self.unprocessed = response
                    response = ""
                else:
                    reasoning += response
                    response = ""
        else:
            for opening_tag, closing_tag in self.thinking_pairs:
                if response.startswith(opening_tag):
                    response = response[len(opening_tag):]
                    self.thinking = True
                    self.thinking_tag = closing_tag

                    close_pos = response.find(closing_tag)
                    if close_pos != -1:
                        reasoning += response[:close_pos]
                        response = response[close_pos + len(closing_tag):]
                        self.thinking = False
                        self.thinking_tag = ""
                    else:
                        if self._is_partial_closing_tag(response):
                            self.unprocessed = response
                            response = ""
                        else:
                            reasoning += response
                            response = ""
                    break
                elif len(response) < len(opening_tag) and self._is_partial_opening_tag(response, opening_tag):
                    self.unprocessed = response
                    response = ""
                    break

        return ChatChunk(response_delta=response, reasoning_delta=reasoning)

    def _is_partial_opening_tag(self, text: str, opening_tag: str) -> bool:
        for i in range(1, len(opening_tag)):
            if text == opening_tag[:i]:
                return True
        return False

    def _is_partial_closing_tag(self, text: str) -> bool:
        if not self.thinking_tag or not text:
            return False
        max_check = min(len(text), len(self.thinking_tag) - 1)
        for i in range(1, max_check + 1):
            if text.endswith(self.thinking_tag[:i]):
                return True
        return False

    def output(self) -> ChatChunk:
        """Returns the final accumulated result.

        Returns:
            A ChatChunk containing the complete reasoning and response.
        """
        response = self.response
        reasoning = self.reasoning
        if self.unprocessed:
            if reasoning and not response:
                reasoning += self.unprocessed
            else:
                response += self.unprocessed
        return ChatChunk(response_delta=response, reasoning_delta=reasoning)


rate_limiters: dict[str, RateLimiter] = {}
api_keys_round_robin: dict[str, int] = {}


def get_api_key(service: str) -> str:
    """Gets the API key for a given service.

    This function supports round-robin API key usage if multiple keys are
    provided in a comma-separated string.

    Args:
        service: The name of the service.

    Returns:
        The API key.
    """
    # get api key for the service
    key = (
        dotenv.get_dotenv_value(f"API_KEY_{service.upper()}")
        or dotenv.get_dotenv_value(f"{service.upper()}_API_KEY")
        or dotenv.get_dotenv_value(f"{service.upper()}_API_TOKEN")
        or "None"
    )
    # if the key contains a comma, use round-robin
    if "," in key:
        api_keys = [k.strip() for k in key.split(",") if k.strip()]
        api_keys_round_robin[service] = api_keys_round_robin.get(service, -1) + 1
        key = api_keys[api_keys_round_robin[service] % len(api_keys)]
    return key


def get_rate_limiter(
    provider: str, name: str, requests: int, input: int, output: int
) -> RateLimiter:
    """Gets or creates a rate limiter for a given model.

    Args:
        provider: The model provider.
        name: The model name.
        requests: The maximum number of requests per minute.
        input: The maximum number of input tokens per minute.
        output: The maximum number of output tokens per minute.

    Returns:
        A RateLimiter instance.
    """
    key = f"{provider}\\{name}"
    rate_limiters[key] = limiter = rate_limiters.get(key, RateLimiter(seconds=60))
    limiter.limits["requests"] = requests or 0
    limiter.limits["input"] = input or 0
    limiter.limits["output"] = output or 0
    return limiter


def _is_transient_litellm_error(exc: Exception) -> bool:
    """Checks if a LiteLLM exception is transient.

    This function uses the status code when available, otherwise it falls back
    to the exception type.

    Args:
        exc: The exception to check.

    Returns:
        True if the error is transient, False otherwise.
    """
    # Prefer explicit status codes if present
    status_code = getattr(exc, "status_code", None)
    if isinstance(status_code, int):
        if status_code in (408, 429, 500, 502, 503, 504):
            return True
        # Treat other 5xx as retriable
        if status_code >= 500:
            return True
        return False

    # Fallback to exception classes mapped by LiteLLM/OpenAI
    transient_types = (
        getattr(openai, "APITimeoutError", Exception),
        getattr(openai, "APIConnectionError", Exception),
        getattr(openai, "RateLimitError", Exception),
        getattr(openai, "APIError", Exception),
        getattr(openai, "InternalServerError", Exception),
        # Some providers map overloads to ServiceUnavailable-like errors
        getattr(openai, "APIStatusError", Exception),
    )
    return isinstance(exc, transient_types)


async def apply_rate_limiter(
    model_config: ModelConfig | None,
    input_text: str,
    rate_limiter_callback: (
        Callable[[str, str, int, int], Awaitable[bool]] | None
    ) = None,
):
    """Applies the rate limiter for a model asynchronously.

    Args:
        model_config: The model configuration.
        input_text: The input text to the model.
        rate_limiter_callback: A callback function for the rate limiter.

    Returns:
        The RateLimiter instance.
    """
    if not model_config:
        return
    limiter = get_rate_limiter(
        model_config.provider,
        model_config.name,
        model_config.limit_requests,
        model_config.limit_input,
        model_config.limit_output,
    )
    limiter.add(input=approximate_tokens(input_text))
    limiter.add(requests=1)
    await limiter.wait(rate_limiter_callback)
    return limiter


def apply_rate_limiter_sync(
    model_config: ModelConfig | None,
    input_text: str,
    rate_limiter_callback: (
        Callable[[str, str, int, int], Awaitable[bool]] | None
    ) = None,
):
    """Applies the rate limiter for a model synchronously.

    Args:
        model_config: The model configuration.
        input_text: The input text to the model.
        rate_limiter_callback: A callback function for the rate limiter.
    """
    if not model_config:
        return
    import asyncio, nest_asyncio

    nest_asyncio.apply()
    return asyncio.run(
        apply_rate_limiter(model_config, input_text, rate_limiter_callback)
    )


class LiteLLMChatWrapper(SimpleChatModel):
    """A wrapper for LiteLLM chat models that integrates with LangChain.

    This class provides a unified interface for calling LiteLLM chat models,
    handling message conversion, rate limiting, and streaming.
    """
    model_name: str
    provider: str
    kwargs: dict = {}

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
        validate_assignment=False,
    )

    def __init__(
        self,
        model: str,
        provider: str,
        model_config: Optional[ModelConfig] = None,
        **kwargs: Any,
    ):
        """Initializes the LiteLLMChatWrapper.

        Args:
            model: The name of the model.
            provider: The name of the provider.
            model_config: The model configuration.
            **kwargs: Additional keyword arguments for the model.
        """
        model_value = f"{provider}/{model}"
        super().__init__(model_name=model_value, provider=provider, kwargs=kwargs)  # type: ignore
        # Set A0 model config as instance attribute after parent init
        self.a0_model_conf = model_config

    @property
    def _llm_type(self) -> str:
        return "litellm-chat"

    def _convert_messages(self, messages: List[BaseMessage]) -> List[dict]:
        """Converts LangChain messages to the LiteLLM format."""
        result = []
        # Map LangChain message types to LiteLLM roles
        role_mapping = {
            "human": "user",
            "ai": "assistant",
            "system": "system",
            "tool": "tool",
        }
        for m in messages:
            role = role_mapping.get(m.type, m.type)
            message_dict = {"role": role, "content": m.content}

            # Handle tool calls for AI messages
            tool_calls = getattr(m, "tool_calls", None)
            if tool_calls:
                # Convert LangChain tool calls to LiteLLM format
                new_tool_calls = []
                for tool_call in tool_calls:
                    # Ensure arguments is a JSON string
                    args = tool_call["args"]
                    if isinstance(args, dict):
                        import json

                        args_str = json.dumps(args)
                    else:
                        args_str = str(args)

                    new_tool_calls.append(
                        {
                            "id": tool_call.get("id", ""),
                            "type": "function",
                            "function": {
                                "name": tool_call["name"],
                                "arguments": args_str,
                            },
                        }
                    )
                message_dict["tool_calls"] = new_tool_calls

            # Handle tool call ID for ToolMessage
            tool_call_id = getattr(m, "tool_call_id", None)
            if tool_call_id:
                message_dict["tool_call_id"] = tool_call_id

            result.append(message_dict)
        return result

    def _call(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Makes a non-streaming call to the model."""
        import asyncio

        msgs = self._convert_messages(messages)

        # Apply rate limiting if configured
        apply_rate_limiter_sync(self.a0_model_conf, str(msgs))

        # Call the model
        resp = completion(
            model=self.model_name, messages=msgs, stop=stop, **{**self.kwargs, **kwargs}
        )

        # Parse output
        parsed = _parse_chunk(resp)
        output = ChatGenerationResult(parsed).output()
        return output["response_delta"]

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Makes a streaming call to the model."""
        import asyncio

        msgs = self._convert_messages(messages)

        # Apply rate limiting if configured
        apply_rate_limiter_sync(self.a0_model_conf, str(msgs))

        result = ChatGenerationResult()

        for chunk in completion(
            model=self.model_name,
            messages=msgs,
            stream=True,
            stop=stop,
            **{**self.kwargs, **kwargs},
        ):
            # parse chunk
            parsed = _parse_chunk(chunk) # chunk parsing
            output = result.add_chunk(parsed) # chunk processing

            # Only yield chunks with non-None content
            if output["response_delta"]:
                yield ChatGenerationChunk(
                    message=AIMessageChunk(content=output["response_delta"])
                )

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """Makes an asynchronous streaming call to the model."""
        msgs = self._convert_messages(messages)

        # Apply rate limiting if configured
        await apply_rate_limiter(self.a0_model_conf, str(msgs))

        result = ChatGenerationResult()

        response = await acompletion(
            model=self.model_name,
            messages=msgs,
            stream=True,
            stop=stop,
            **{**self.kwargs, **kwargs},
        )
        async for chunk in response:  # type: ignore
            # parse chunk
            parsed = _parse_chunk(chunk) # chunk parsing
            output = result.add_chunk(parsed) # chunk processing

            # Only yield chunks with non-None content
            if output["response_delta"]:
                yield ChatGenerationChunk(
                    message=AIMessageChunk(content=output["response_delta"])
                )

    async def unified_call(
        self,
        system_message="",
        user_message="",
        messages: List[BaseMessage] | None = None,
        response_callback: Callable[[str, str], Awaitable[None]] | None = None,
        reasoning_callback: Callable[[str, str], Awaitable[None]] | None = None,
        tokens_callback: Callable[[str, int], Awaitable[None]] | None = None,
        rate_limiter_callback: (
            Callable[[str, str, int, int], Awaitable[bool]] | None
        ) = None,
        **kwargs: Any,
    ) -> Tuple[str, str]:
        """A unified method for calling the model with streaming and callbacks.

        Args:
            system_message: The system message.
            user_message: The user message.
            messages: A list of messages to send to the model.
            response_callback: A callback for the response stream.
            reasoning_callback: A callback for the reasoning stream.
            tokens_callback: A callback for the token count.
            rate_limiter_callback: A callback for the rate limiter.
            **kwargs: Additional keyword arguments for the model.

        Returns:
            A tuple containing the response and reasoning from the model.
        """
        turn_off_logging()

        if not messages:
            messages = []
        # construct messages
        if system_message:
            messages.insert(0, SystemMessage(content=system_message))
        if user_message:
            messages.append(HumanMessage(content=user_message))

        # convert to litellm format
        msgs_conv = self._convert_messages(messages)

        # Apply rate limiting if configured
        limiter = await apply_rate_limiter(
            self.a0_model_conf, str(msgs_conv), rate_limiter_callback
        )

        # Prepare call kwargs and retry config (strip A0-only params before calling LiteLLM)
        call_kwargs: dict[str, Any] = {**self.kwargs, **kwargs}
        max_retries: int = int(call_kwargs.pop("a0_retry_attempts", 2))
        retry_delay_s: float = float(call_kwargs.pop("a0_retry_delay_seconds", 1.5))
        stream = reasoning_callback is not None or response_callback is not None or tokens_callback is not None

        # results
        result = ChatGenerationResult()

        attempt = 0
        while True:
            got_any_chunk = False
            try:
                # call model
                _completion = await acompletion(
                    model=self.model_name,
                    messages=msgs_conv,
                    stream=stream,
                    **call_kwargs,
                )

                if stream:
                    # iterate over chunks
                    async for chunk in _completion:  # type: ignore
                        got_any_chunk = True
                        # parse chunk
                        parsed = _parse_chunk(chunk)
                        output = result.add_chunk(parsed)

                        # collect reasoning delta and call callbacks
                        if output["reasoning_delta"]:
                            if reasoning_callback:
                                await reasoning_callback(output["reasoning_delta"], result.reasoning)
                            if tokens_callback:
                                await tokens_callback(
                                    output["reasoning_delta"],
                                    approximate_tokens(output["reasoning_delta"]),
                                )
                            # Add output tokens to rate limiter if configured
                            if limiter:
                                limiter.add(output=approximate_tokens(output["reasoning_delta"]))
                        # collect response delta and call callbacks
                        if output["response_delta"]:
                            if response_callback:
                                await response_callback(output["response_delta"], result.response)
                            if tokens_callback:
                                await tokens_callback(
                                    output["response_delta"],
                                    approximate_tokens(output["response_delta"]),
                                )
                            # Add output tokens to rate limiter if configured
                            if limiter:
                                limiter.add(output=approximate_tokens(output["response_delta"]))

                # non-stream response
                else:
                    parsed = _parse_chunk(_completion)
                    output = result.add_chunk(parsed)
                    if limiter:
                        if output["response_delta"]:
                            limiter.add(output=approximate_tokens(output["response_delta"]))
                        if output["reasoning_delta"]:
                            limiter.add(output=approximate_tokens(output["reasoning_delta"]))

                # Successful completion of stream
                return result.response, result.reasoning

            except Exception as e:
                import asyncio

                # Retry only if no chunks received and error is transient
                if got_any_chunk or not _is_transient_litellm_error(e) or attempt >= max_retries:
                    raise
                attempt += 1
                await asyncio.sleep(retry_delay_s)


class AsyncAIChatReplacement:
    """A replacement for the AI chat client that uses an async wrapper."""
    class _Completions:
        def __init__(self, wrapper):
            self._wrapper = wrapper

        async def create(self, *args, **kwargs):
            # call the async _acall method on the wrapper
            return await self._wrapper._acall(*args, **kwargs)

    class _Chat:
        def __init__(self, wrapper):
            self.completions = AsyncAIChatReplacement._Completions(wrapper)

    def __init__(self, wrapper, *args, **kwargs):
        """Initializes the AsyncAIChatReplacement.

        Args:
            wrapper: The wrapper to use for making async calls.
        """
        self._wrapper = wrapper
        self.chat = AsyncAIChatReplacement._Chat(wrapper)


from browser_use.llm import ChatOllama, ChatOpenRouter, ChatGoogle, ChatAnthropic, ChatGroq, ChatOpenAI

class BrowserCompatibleChatWrapper(ChatOpenRouter):
    """A browser-compatible chat wrapper.

    This class extends the ChatOpenRouter to provide a browser-compatible
    interface for the LiteLLMChatWrapper. It handles message filtering and
    sanitization before sending them to the LLM.
    """

    def __init__(self, *args, **kwargs):
        """Initializes the BrowserCompatibleChatWrapper.

        Args:
            *args: Positional arguments for the LiteLLMChatWrapper.
            **kwargs: Keyword arguments for the LiteLLMChatWrapper.
        """
        turn_off_logging()
        # Create the underlying LiteLLM wrapper
        self._wrapper = LiteLLMChatWrapper(*args, **kwargs)
        # Browser-use may expect a 'model' attribute
        self.model = self._wrapper.model_name
        self.kwargs = self._wrapper.kwargs

    @property
    def model_name(self) -> str:
        """The name of the model."""
        return self._wrapper.model_name

    @property
    def provider(self) -> str:
        """The provider of the model."""
        return self._wrapper.provider

    def get_client(self, *args, **kwargs):  # type: ignore
        """Gets the async AI chat client."""
        return AsyncAIChatReplacement(self, *args, **kwargs)

    async def _acall(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ):
        """Makes an asynchronous call to the model."""
        # Apply rate limiting if configured
        apply_rate_limiter_sync(self._wrapper.a0_model_conf, str(messages))

        # Call the model
        try:
            model = kwargs.pop("model", None)
            kwrgs = {**self._wrapper.kwargs, **kwargs}

            # hack from browser-use to fix json schema for gemini (additionalProperties, $defs, $ref)
            if "response_format" in kwrgs and "json_schema" in kwrgs["response_format"] and model.startswith("gemini/"):
                kwrgs["response_format"]["json_schema"] = ChatGoogle("")._fix_gemini_schema(kwrgs["response_format"]["json_schema"])

            resp = await acompletion(
                model=self._wrapper.model_name,
                messages=messages,
                stop=stop,
                **kwrgs,
            )

            # Gemini: strip triple backticks and conform schema
            try:
                msg = resp.choices[0].message # type: ignore
                if self.provider == "gemini" and isinstance(getattr(msg, "content", None), str):
                    cleaned = browser_use_monkeypatch.gemini_clean_and_conform(msg.content) # type: ignore
                    if cleaned:
                        msg.content = cleaned
            except Exception:
                pass

        except Exception as e:
            raise e

        # another hack for browser-use post process invalid jsons
        try:
            if "response_format" in kwrgs and "json_schema" in kwrgs["response_format"] or "json_object" in kwrgs["response_format"]:
                if resp.choices[0].message.content is not None and not resp.choices[0].message.content.startswith("{"): # type: ignore
                    js = dirty_json.parse(resp.choices[0].message.content) # type: ignore
                    resp.choices[0].message.content = dirty_json.stringify(js) # type: ignore
        except Exception as e:
            pass

        return resp

class LiteLLMEmbeddingWrapper(Embeddings):
    """A wrapper for LiteLLM embedding models that integrates with LangChain."""
    model_name: str
    kwargs: dict = {}
    a0_model_conf: Optional[ModelConfig] = None

    def __init__(
        self,
        model: str,
        provider: str,
        model_config: Optional[ModelConfig] = None,
        **kwargs: Any,
    ):
        """Initializes the LiteLLMEmbeddingWrapper.

        Args:
            model: The name of the model.
            provider: The name of the provider.
            model_config: The model configuration.
            **kwargs: Additional keyword arguments for the model.
        """
        self.model_name = f"{provider}/{model}" if provider != "openai" else model
        self.kwargs = kwargs
        self.a0_model_conf = model_config

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of documents.

        Args:
            texts: A list of documents to embed.

        Returns:
            A list of embeddings.
        """
        # Apply rate limiting if configured
        apply_rate_limiter_sync(self.a0_model_conf, " ".join(texts))

        resp = embedding(model=self.model_name, input=texts, **self.kwargs)
        return [
            item.get("embedding") if isinstance(item, dict) else item.embedding  # type: ignore
            for item in resp.data  # type: ignore
        ]

    def embed_query(self, text: str) -> List[float]:
        """Embeds a single query.

        Args:
            text: The query to embed.

        Returns:
            The embedding for the query.
        """
        # Apply rate limiting if configured
        apply_rate_limiter_sync(self.a0_model_conf, text)

        resp = embedding(model=self.model_name, input=[text], **self.kwargs)
        item = resp.data[0]  # type: ignore
        return item.get("embedding") if isinstance(item, dict) else item.embedding  # type: ignore


class LocalSentenceTransformerWrapper(Embeddings):
    """A local wrapper for sentence-transformers models.

    This class avoids HuggingFace API calls by using a local sentence-
    transformers model.
    """

    def __init__(
        self,
        provider: str,
        model: str,
        model_config: Optional[ModelConfig] = None,
        **kwargs: Any,
    ):
        """Initializes the LocalSentenceTransformerWrapper.

        Args:
            provider: The name of the provider.
            model: The name of the model.
            model_config: The model configuration.
            **kwargs: Additional keyword arguments for the model.
        """
        # Clean common user-input mistakes
        model = model.strip().strip('"').strip("'")

        # Remove the "sentence-transformers/" prefix if present
        if model.startswith("sentence-transformers/"):
            model = model[len("sentence-transformers/") :]

        # Filter kwargs for SentenceTransformer only (no LiteLLM params like 'stream_timeout')
        st_allowed_keys = {
            "device",
            "cache_folder",
            "use_auth_token",
            "revision",
            "trust_remote_code",
            "model_kwargs",
        }
        st_kwargs = {k: v for k, v in (kwargs or {}).items() if k in st_allowed_keys}

        self.model = SentenceTransformer(model, **st_kwargs)
        self.model_name = model
        self.a0_model_conf = model_config

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of documents.

        Args:
            texts: A list of documents to embed.

        Returns:
            A list of embeddings.
        """
        # Apply rate limiting if configured
        apply_rate_limiter_sync(self.a0_model_conf, " ".join(texts))

        embeddings = self.model.encode(texts, convert_to_tensor=False)  # type: ignore
        return embeddings.tolist() if hasattr(embeddings, "tolist") else embeddings  # type: ignore

    def embed_query(self, text: str) -> List[float]:
        """Embeds a single query.

        Args:
            text: The query to embed.

        Returns:
            The embedding for the query.
        """
        # Apply rate limiting if configured
        apply_rate_limiter_sync(self.a0_model_conf, text)

        embedding = self.model.encode([text], convert_to_tensor=False)  # type: ignore
        result = (
            embedding[0].tolist() if hasattr(embedding[0], "tolist") else embedding[0]
        )
        return result  # type: ignore


def _get_litellm_chat(
    cls: type = LiteLLMChatWrapper,
    model_name: str = "",
    provider_name: str = "",
    model_config: Optional[ModelConfig] = None,
    **kwargs: Any,
):
    """Gets a LiteLLM chat model instance.

    Args:
        cls: The class to instantiate.
        model_name: The name of the model.
        provider_name: The name of the provider.
        model_config: The model configuration.
        **kwargs: Additional keyword arguments for the model.

    Returns:
        An instance of the chat model class.
    """
    # use api key from kwargs or env
    api_key = kwargs.pop("api_key", None) or get_api_key(provider_name)

    # Only pass API key if key is not a placeholder
    if api_key and api_key not in ("None", "NA"):
        kwargs["api_key"] = api_key

    provider_name, model_name, kwargs = _adjust_call_args(
        provider_name, model_name, kwargs
    )
    return cls(
        provider=provider_name, model=model_name, model_config=model_config, **kwargs
    )


def _get_litellm_embedding(
    model_name: str,
    provider_name: str,
    model_config: Optional[ModelConfig] = None,
    **kwargs: Any,
):
    """Gets a LiteLLM embedding model instance.

    Args:
        model_name: The name of the model.
        provider_name: The name of the provider.
        model_config: The model configuration.
        **kwargs: Additional keyword arguments for the model.

    Returns:
        An instance of the embedding model class.
    """
    # Check if this is a local sentence-transformers model
    if provider_name == "huggingface" and model_name.startswith(
        "sentence-transformers/"
    ):
        # Use local sentence-transformers instead of LiteLLM for local models
        provider_name, model_name, kwargs = _adjust_call_args(
            provider_name, model_name, kwargs
        )
        return LocalSentenceTransformerWrapper(
            provider=provider_name,
            model=model_name,
            model_config=model_config,
            **kwargs,
        )

    # use api key from kwargs or env
    api_key = kwargs.pop("api_key", None) or get_api_key(provider_name)

    # Only pass API key if key is not a placeholder
    if api_key and api_key not in ("None", "NA"):
        kwargs["api_key"] = api_key

    provider_name, model_name, kwargs = _adjust_call_args(
        provider_name, model_name, kwargs
    )
    return LiteLLMEmbeddingWrapper(
        model=model_name, provider=provider_name, model_config=model_config, **kwargs
    )


def _parse_chunk(chunk: Any) -> ChatChunk:
    """Parses a chunk from the LiteLLM response.

    Args:
        chunk: The chunk to parse.

    Returns:
        A ChatChunk containing the response and reasoning deltas.
    """
    delta = chunk["choices"][0].get("delta", {})
    message = chunk["choices"][0].get("message", {}) or chunk["choices"][0].get(
        "model_extra", {}
    ).get("message", {})
    response_delta = (
        delta.get("content", "")
        if isinstance(delta, dict)
        else getattr(delta, "content", "")
    ) or (
        message.get("content", "")
        if isinstance(message, dict)
        else getattr(message, "content", "")
    )
    reasoning_delta = (
        delta.get("reasoning_content", "")
        if isinstance(delta, dict)
        else getattr(delta, "reasoning_content", "")
    ) or (
        message.get("reasoning_content", "")
        if isinstance(message, dict)
        else getattr(message, "reasoning_content", "")
    )

    return ChatChunk(reasoning_delta=reasoning_delta, response_delta=response_delta)



def _adjust_call_args(provider_name: str, model_name: str, kwargs: dict):
    """Adjusts the arguments for a LiteLLM call.

    Args:
        provider_name: The name of the provider.
        model_name: The name of the model.
        kwargs: The keyword arguments.

    Returns:
        A tuple containing the adjusted provider name, model name, and kwargs.
    """
    # for openrouter add app reference
    if provider_name == "openrouter":
        kwargs["extra_headers"] = {
            "HTTP-Referer": "https://agent-zero.ai",
            "X-Title": "Agent Zero",
        }

    # remap other to openai for litellm
    if provider_name == "other":
        provider_name = "openai"

    return provider_name, model_name, kwargs


def _merge_provider_defaults(
    provider_type: str, original_provider: str, kwargs: dict
) -> tuple[str, dict]:
    """Merges provider default settings.

    Args:
        provider_type: The type of the provider (e.g., 'chat', 'embedding').
        original_provider: The original provider name.
        kwargs: The keyword arguments.

    Returns:
        A tuple containing the merged provider name and kwargs.
    """
    # Normalize .env-style numeric strings (e.g., "timeout=30") into ints/floats for LiteLLM
    def _normalize_values(values: dict) -> dict:
        result: dict[str, Any] = {}
        for k, v in values.items():
            if isinstance(v, str):
                try:
                    result[k] = int(v)
                except ValueError:
                    try:
                        result[k] = float(v)
                    except ValueError:
                        result[k] = v
            else:
                result[k] = v
        return result

    provider_name = original_provider  # default: unchanged
    cfg = get_provider_config(provider_type, original_provider)
    if cfg:
        provider_name = cfg.get("litellm_provider", original_provider).lower()

        # Extra arguments nested under `kwargs` for readability
        extra_kwargs = cfg.get("kwargs") if isinstance(cfg, dict) else None  # type: ignore[arg-type]
        if isinstance(extra_kwargs, dict):
            for k, v in extra_kwargs.items():
                kwargs.setdefault(k, v)

    # Inject API key based on the *original* provider id if still missing
    if "api_key" not in kwargs:
        key = get_api_key(original_provider)
        if key and key not in ("None", "NA"):
            kwargs["api_key"] = key

    # Merge LiteLLM global kwargs (timeouts, stream_timeout, etc.)
    try:
        global_kwargs = settings.get_settings().get("litellm_global_kwargs", {})  # type: ignore[union-attr]
    except Exception:
        global_kwargs = {}
    if isinstance(global_kwargs, dict):
        for k, v in _normalize_values(global_kwargs).items():
            kwargs.setdefault(k, v)

    return provider_name, kwargs


def get_chat_model(
    provider: str, name: str, model_config: Optional[ModelConfig] = None, **kwargs: Any
) -> LiteLLMChatWrapper:
    """Gets a chat model.

    Args:
        provider: The name of the provider.
        name: The name of the model.
        model_config: The model configuration.
        **kwargs: Additional keyword arguments for the model.

    Returns:
        An instance of the chat model.
    """
    orig = provider.lower()
    provider_name, kwargs = _merge_provider_defaults("chat", orig, kwargs)
    return _get_litellm_chat(
        LiteLLMChatWrapper, name, provider_name, model_config, **kwargs
    )


def get_browser_model(
    provider: str, name: str, model_config: Optional[ModelConfig] = None, **kwargs: Any
) -> BrowserCompatibleChatWrapper:
    """Gets a browser-compatible chat model.

    Args:
        provider: The name of the provider.
        name: The name of the model.
        model_config: The model configuration.
        **kwargs: Additional keyword arguments for the model.

    Returns:
        An instance of the browser-compatible chat model.
    """
    orig = provider.lower()
    provider_name, kwargs = _merge_provider_defaults("chat", orig, kwargs)
    return _get_litellm_chat(
        BrowserCompatibleChatWrapper, name, provider_name, model_config, **kwargs
    )


def get_embedding_model(
    provider: str, name: str, model_config: Optional[ModelConfig] = None, **kwargs: Any
) -> LiteLLMEmbeddingWrapper | LocalSentenceTransformerWrapper:
    """Gets an embedding model.

    Args:
        provider: The name of the provider.
        name: The name of the model.
        model_config: The model configuration.
        **kwargs: Additional keyword arguments for the model.

    Returns:
        An instance of the embedding model.
    """
    orig = provider.lower()
    provider_name, kwargs = _merge_provider_defaults("embedding", orig, kwargs)
    return _get_litellm_embedding(name, provider_name, model_config, **kwargs)

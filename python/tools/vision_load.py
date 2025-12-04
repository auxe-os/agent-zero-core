import base64
from python.helpers.print_style import PrintStyle
from python.helpers.tool import Tool, Response
from python.helpers import runtime, files, images
from mimetypes import guess_type
from python.helpers import history

# image optimization and token estimation for context window
MAX_PIXELS = 768_000
QUALITY = 75
TOKENS_ESTIMATE = 1500


class VisionLoad(Tool):
    async def execute(self, paths: list[str] | None = None, **kwargs) -> Response:

        self.images_dict = {}
        template: list[dict[str, str]] = []  # type: ignore

        # Normalize paths to avoid mutable default issues
        paths = paths or []

        for path in paths:
            if not await runtime.call_development_function(files.exists, str(path)):
                continue

            if path not in self.images_dict:
                mime_type, _ = guess_type(str(path))
                if mime_type and mime_type.startswith("image/"):
                    try:
                        # Read binary file
                        file_content = await runtime.call_development_function(
                            files.read_file_base64, str(path)
                        )
                        file_content = base64.b64decode(file_content)
                        # Compress and convert to JPEG
                        compressed = images.compress_image(
                            file_content, max_pixels=MAX_PIXELS, quality=QUALITY
                        )
                        # Encode as base64
                        file_content_b64 = base64.b64encode(compressed).decode("utf-8")

                        # DEBUG: Save compressed image
                        # await runtime.call_development_function(
                        #     files.write_file_base64, str(path), file_content_b64
                        # )

                        # Construct the data URL (always JPEG after compression)
                        self.images_dict[path] = file_content_b64
                    except Exception as e:
                        self.images_dict[path] = None
                        PrintStyle().error(f"Error processing image {path}: {e}")
                        if hasattr(self.agent, "context") and hasattr(self.agent.context, "log"):
                            try:
                                self.agent.context.log.log("warning", f"Error processing image {path}: {e}")
                            except Exception:
                                # Fallback to simple print if structured logging fails
                                PrintStyle().print(f"Warning: error logged for image {path}: {e}")

        # Provide a more meaningful message based on how many images were processed/queued
        if not self.images_dict:
            message = "No images found at provided paths"
        else:
            message = f"{len(self.images_dict)} image(s) queued for vision analysis"

        return Response(message=message, break_loop=False)

    def _model_supports_image_url(self) -> bool:
        """Return True only for models that can handle OpenAI-style image_url content.

        Deepseek currently does not accept image_url variants in messages, so we
        explicitly disable image payloads for it and fall back to text-only.
        """
        try:
            from python.helpers import settings  # type: ignore

            current = getattr(settings, "current_settings", {})  # type: ignore[assignment]
            provider = str(current.get("chat_model_provider", ""))
        except Exception:
            # If settings cannot be read for any reason, be conservative and
            # avoid sending image_url payloads.
            return False

        # Deepseek models use a JSON schema that rejects image_url variants.
        if provider == "deepseek":
            return False

        # For now, assume non-Deepseek chat providers configured as vision-capable
        # can handle image_url payloads.
        return True

    async def after_execution(self, response: Response, **kwargs):

        # build image data messages for LLMs, or error message
        if not self.images_dict:
            self.agent.hist_add_tool_result(self.name, "No images processed")

            # print and log short version
            message = "No images processed"
            PrintStyle(
                font_color="#1B4F72", background_color="white", padding=True, bold=True
            ).print(f"{self.agent.agent_name}: Response from tool '{self.name}'")
            PrintStyle(font_color="#85C1E9").print(message)
            self.log.update(result=message)
            return

        if self._model_supports_image_url():
            # Original behavior: send image_url payloads so vision-capable models
            # can see images directly.
            content = []  # type: ignore[var-annotated]
            for path, image in self.images_dict.items():
                if image:
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                        }
                    )
                else:
                    content.append(
                        {
                            "type": "text",
                            "text": "Error processing image " + path,
                        }
                    )

            # append as raw message content for LLMs with vision tokens estimate
            msg = history.RawMessage(  # type: ignore[arg-type]
                raw_content=content, preview="<Base64 encoded image data>"
            )
            self.agent.hist_add_message(
                False, content=msg, tokens=TOKENS_ESTIMATE * len(content)
            )
        else:
            # Fallback: plain-text summary for models that don't support image_url,
            # such as Deepseek.
            summary_lines: list[str] = []
            for path, image in self.images_dict.items():
                if image:
                    summary_lines.append(f"[vision] Loaded image for analysis: {path}")
                else:
                    summary_lines.append(f"[vision] Error processing image {path}")

            # Append plain-text summary for all models (avoids image_url payloads that
            # Deepseek and some other providers don't support)
            summary_text = "\n".join(summary_lines)
            self.agent.hist_add_message(
                False,
                content=(
                    "Vision tool summary (no direct image payloads sent to model):\n"
                    f"{summary_text}"
                ),
                tokens=TOKENS_ESTIMATE * len(self.images_dict),
            )

        # print and log short version
        message = f"{len(self.images_dict)} images processed"
        PrintStyle(
            font_color="#1B4F72", background_color="white", padding=True, bold=True
        ).print(f"{self.agent.agent_name}: Response from tool '{self.name}'")
        PrintStyle(font_color="#85C1E9").print(message)
        self.log.update(result=message)

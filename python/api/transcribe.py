from python.helpers.api import ApiHandler, Request, Response

from python.helpers import runtime, settings, whisper


class Transcribe(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        audio = input.get("audio")
        ctxid = input.get("ctxid", "")

        if ctxid:
            context = self.use_context(ctxid)
        else:
            context = None

        # if not await whisper.is_downloaded():
        #     context.log.log(type="info", content="Whisper STT model is currently being initialized, please wait...")

        set = settings.get_settings()

        try:
            result = await whisper.transcribe(set["stt_model_size"], audio)  # type: ignore
            return result
        except FileNotFoundError as e:
            # Common case: ffmpeg not installed or not on PATH for the current environment.
            msg = str(e)
            if "ffmpeg" in msg:
                friendly = (
                    "Speech-to-text requires the 'ffmpeg' binary to be installed and available in PATH. "
                    "Please install ffmpeg (e.g. via Homebrew: 'brew install ffmpeg') and restart Agent Zero."
                )
                if context is not None:
                    context.log.log(type="error", content=friendly)
                return {"success": False, "error": friendly}
            raise

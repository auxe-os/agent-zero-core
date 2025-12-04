# kokoro_tts.py

import base64
import io
import warnings
import asyncio
import soundfile as sf
from python.helpers.print_style import PrintStyle

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import threading

_pipeline = None
_speed = 1.1
_loading = False
_synth_lock = threading.Lock()  # Thread lock to prevent concurrent synthesis


async def preload():
    """Load the Kokoro TTS model. Safe to call multiple times."""
    return await _preload()


async def _preload():
    global _pipeline, _loading

    # Wait if another call is already loading
    if _loading:
        return
    
    # Already loaded
    if _pipeline is not None:
        return

    with _synth_lock:
        # Double-check inside lock
        if _pipeline is not None:
            return
            
        try:
            _loading = True
            PrintStyle.standard("Loading Kokoro TTS model...")
            from kokoro import KPipeline
            _pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
            PrintStyle.standard("Kokoro TTS model loaded successfully.")
        except ImportError as e:
            PrintStyle.error(f"Kokoro TTS not available: {e}")
            PrintStyle.standard("Install with: pip install kokoro>=0.9.2")
            raise
        except Exception as e:
            PrintStyle.error(f"Failed to load Kokoro TTS: {e}")
            raise
        finally:
            _loading = False


async def is_downloading():
    """Check if the model is currently being downloaded/loaded."""
    return _loading


def is_downloaded():
    """Check if the model is already loaded."""
    return _pipeline is not None


async def synthesize_sentences(sentences: list[str]):
    """Generate audio for multiple sentences and return concatenated base64 audio."""
    from python.helpers import settings
    
    # Read voice once at start of request
    voice = settings.get_settings().get("tts_kokoro_voice", "af_bella")
    
    # Ensure model is loaded before offloading to thread
    await _preload()
    
    # Serialize synthesis to prevent concurrent issues
    # Use run_in_executor to avoid blocking the async loop with the lock and heavy computation
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _synthesize_sentences_sync, sentences, voice)


def _synthesize_sentences_sync(sentences: list[str], voice: str = "af_bella"):
    """Synchronous wrapper for synthesis to run in thread pool."""
    with _synth_lock:
        PrintStyle.standard(f"TTS: {voice}")
        
        # Ensure loaded
        if _pipeline is None:
             # This calls async _preload but we need sync here. 
             # However, _preload check is fast if loaded.
             # Since we are in a thread, we can't await. 
             # But _preload is now async. We should ensure preload is called before offloading.
             raise RuntimeError("Kokoro TTS model not loaded")

        combined_audio = []
        
        try:
            for sentence in sentences:
                text = sentence.strip()
                if not text:
                    continue
                    
                for segment in _pipeline(text, voice=voice, speed=_speed):  # type: ignore
                    audio_numpy = segment.audio.detach().cpu().numpy()
                    combined_audio.extend(audio_numpy)

            # Handle empty audio
            if not combined_audio:
                return ""

            # Convert to WAV bytes
            with io.BytesIO() as buffer:
                sf.write(buffer, combined_audio, 24000, format="WAV")
                return base64.b64encode(buffer.getvalue()).decode("utf-8")

        except Exception as e:
            PrintStyle.error(f"Kokoro TTS synthesis error: {e}")
            raise


async def _synthesize_sentences(sentences: list[str], voice: str = "af_bella"):
    # Deprecated/Unused in favor of threaded execution
    pass    
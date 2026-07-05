"""
CivicTrust AI - Voice Module
Speech-to-text and text-to-speech capabilities.
"""
import logging
from typing import Dict, Any, Optional
import base64

logger = logging.getLogger(__name__)


class VoiceModule:
    """Handles speech recognition and synthesis."""

    def __init__(self):
        self.asr_model = None
        self.tts_model = None

    async def speech_to_text(self, audio_base64: str, language: str = "id") -> Dict[str, Any]:
        """Convert speech audio to text."""
        try:
            # Try using whisper
            text = await self._transcribe_with_whisper(audio_base64, language)
            
            return {
                "text": text,
                "language": language,
                "confidence": 0.85 if text else 0.0,
            }
        except ImportError:
            logger.warning("Whisper not installed, returning placeholder")
            return {
                "text": "",
                "language": language,
                "confidence": 0.0,
                "note": "Speech recognition tidak tersedia. Install openai-whisper untuk fitur ini.",
            }
        except Exception as e:
            logger.error(f"Speech-to-text failed: {e}")
            return {
                "text": "",
                "language": language,
                "confidence": 0.0,
                "error": str(e),
            }

    async def text_to_speech(self, text: str, language: str = "id") -> Optional[str]:
        """Convert text to speech audio (returns base64 encoded audio)."""
        try:
            audio_base64 = await self._synthesize_with_tts(text, language)
            return audio_base64
        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}")
            return None

    async def _transcribe_with_whisper(self, audio_base64: str, language: str) -> str:
        """Transcribe audio using OpenAI Whisper."""
        try:
            import whisper

            if self.asr_model is None:
                from app.config import settings
                self.asr_model = whisper.load_model(settings.WHISPER_MODEL)

            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_base64)
            
            # Save to temp file and transcribe
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            try:
                result = self.asr_model.transcribe(tmp_path, language=language if language != "id" else None)
                return result["text"].strip()
            finally:
                os.unlink(tmp_path)

        except ImportError:
            raise ImportError("openai-whisper not installed")
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return ""

    async def _synthesize_with_tts(self, text: str, language: str) -> str:
        """Synthesize speech from text using TTS."""
        try:
            from TTS.api import TTS
            import tempfile
            import os

            if self.tts_model is None:
                from app.config import settings
                self.tts_model = TTS(settings.TTS_MODEL, gpu=False)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp_path = tmp.name

            try:
                self.tts_model.tts_to_file(text=text, file_path=tmp_path)
                
                with open(tmp_path, "rb") as f:
                    audio_bytes = f.read()
                
                return base64.b64encode(audio_bytes).decode("utf-8")
            finally:
                os.unlink(tmp_path)

        except ImportError:
            raise ImportError("TTS not installed")
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return ""
"""
CivicTrust AI - Translation Module
Multi-language translation support (ID, EN, FR, JA, AR).
"""
import logging
from app.utils.llm import get_llm

logger = logging.getLogger(__name__)

TRANSLATION_PROMPT = """Translate the following text from {source_lang} to {target_lang}.

Text: {text}

Translation:"""


class TranslationModule:
    """Handles text translation between supported languages."""

    def __init__(self):
        self.llm = get_llm()
        self.supported_languages = {
            "id": "Indonesian",
            "en": "English",
            "fr": "French",
            "ja": "Japanese",
            "ar": "Arabic",
        }

    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text from source language to target language."""
        if source_lang == target_lang:
            return text

        try:
            source_name = self.supported_languages.get(source_lang, source_lang)
            target_name = self.supported_languages.get(target_lang, target_lang)

            prompt = TRANSLATION_PROMPT.format(
                source_lang=source_name,
                target_lang=target_name,
                text=text,
            )

            translated = await self.llm.generate(prompt)
            return translated.strip()

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text

    async def detect_language(self, text: str) -> str:
        """Detect the language of the text."""
        try:
            prompt = f"Detect the language of this text and return only the language code (id, en, fr, ja, ar): {text[:200]}"
            response = await self.llm.generate(prompt)
            lang = response.strip().lower()[:2]
            return lang if lang in self.supported_languages else "id"
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return "id"
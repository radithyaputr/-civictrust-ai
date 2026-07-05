"""
CivicTrust AI - Vision Module
OCR and image analysis for document verification.
"""
import logging
from typing import Dict, Any
from io import BytesIO

logger = logging.getLogger(__name__)


class VisionModule:
    """Handles image processing and OCR."""

    def __init__(self):
        self.ocr_engine = None

    async def extract_text(self, image_bytes: bytes, language: str = "id") -> Dict[str, Any]:
        """Extract text from an image using OCR."""
        try:
            # Try to use easyocr as primary OCR engine
            text = await self._ocr_with_easyocr(image_bytes, language)
            
            return {
                "success": True,
                "extracted_text": text,
                "language": language,
                "method": "easyocr",
                "word_count": len(text.split()) if text else 0,
            }
        except ImportError:
            # Fallback: return placeholder
            logger.warning("OCR libraries not installed, returning placeholder")
            return {
                "success": False,
                "extracted_text": "",
                "language": language,
                "method": "unavailable",
                "word_count": 0,
                "note": "OCR engine tidak tersedia. Install easyocr atau tesseract untuk fitur ini.",
            }
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return {
                "success": False,
                "extracted_text": "",
                "language": language,
                "method": "error",
                "word_count": 0,
                "error": str(e),
            }

    async def _ocr_with_easyocr(self, image_bytes: bytes, language: str) -> str:
        """Perform OCR using easyocr."""
        try:
            import easyocr
            import numpy as np
            from PIL import Image

            if self.ocr_engine is None:
                lang_list = ["id", "en"]
                if language == "ja":
                    lang_list = ["ja", "en"]
                elif language == "ar":
                    lang_list = ["ar", "en"]
                elif language == "fr":
                    lang_list = ["fr", "en"]
                
                self.ocr_engine = easyocr.Reader(lang_list, gpu=False)

            image = Image.open(BytesIO(image_bytes))
            img_array = np.array(image)
            
            results = self.ocr_engine.readtext(img_array)
            text = " ".join([result[1] for result in results])
            
            return text
        except ImportError:
            raise ImportError("easyocr not installed")
        except Exception as e:
            logger.error(f"EasyOCR failed: {e}")
            return ""

    async def verify_document(self, image_bytes: bytes) -> Dict[str, Any]:
        """Verify a document image for authenticity indicators."""
        text = await self.extract_text(image_bytes)
        
        # Basic document verification logic
        verification_flags = []
        
        if text.get("word_count", 0) == 0:
            verification_flags.append("Tidak ada teks terdeteksi")
        
        return {
            "verified": len(verification_flags) == 0,
            "flags": verification_flags,
            "extracted_text": text.get("extracted_text", ""),
        }
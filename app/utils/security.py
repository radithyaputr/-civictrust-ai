"""
CivicTrust AI - Security Module
Input sanitization, prompt injection detection, and rate limiting helpers.
"""
import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Known prompt injection patterns
INJECTION_PATTERNS = [
    r"(?i)(?:ignore|disregard|forget|override)\s+(?:all\s+)?(?:previous|above|below)?\s*(?:instructions|prompt|commands|directions)",
    r"(?i)(?:you\s+(?:are\s+)?(?:now|must\s+be))\s+(?:a\s+)?(?:free|unlimited|uncensored|jailbroken)",
    r"(?i)(?:system\s*(?:prompt|message|instruction))",
    r"(?i)(?:do\s+(?:not\s+)?(?:follow|use|apply|consider))",
    r"(?i)(?:print|output|show|display|return)\s+(?:the\s+)?(?:system|prompt|instructions)",
    r"(?i)(?:new\s+)?(?:chat|session|conversation|turn)\s*(?:.|:|\n)",
    r"(?i)(?:pretend|assume|act\s+as)",
    r"(?i)(?:${|\$instruction|\$prompt)",
    r"(?i)(?:<script|javascript:|onclick=|onerror=)",
    r"(?i)(?:'.*\s*OR\s*['\"]?1['\"]?\s*=\s*['\"]?1)",
]


def sanitize_input(text: str, max_length: int = 4096) -> str:
    """Sanitize user input: strip dangerous characters and limit length."""
    if not text:
        return ""

    text = text.strip()[:max_length]

    text = text.replace("\x00", "")

    return text


def detect_prompt_injection(text: str) -> Dict[str, Any]:
    """Detect potential prompt injection attempts."""
    flags = []
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            flags.append(f"Pola mencurigakan terdeteksi: {pattern[:50]}")

    return {
        "injection_detected": len(flags) > 0,
        "flags": flags,
        "risk_score": min(len(flags) * 0.3, 1.0),
    }


def validate_language_code(code: str) -> bool:
    """Validate language code against supported list."""
    from app.config import settings
    return code in settings.SUPPORTED_LANGUAGES


def validate_api_key(api_key: str) -> bool:
    """Validate API key against configured keys."""
    from app.config import settings
    if not settings.API_KEY_REQUIRED:
        return True
    if not settings.API_KEYS:
        return False
    return api_key in settings.API_KEYS


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = {}

    def is_allowed(self, key: str) -> bool:
        """Check if a request is allowed for the given key."""
        import time
        now = time.time()
        if key not in self._requests:
            self._requests[key] = []
        self._requests[key] = [t for t in self._requests[key] if now - t < self.window_seconds]
        if len(self._requests[key]) >= self.max_requests:
            return False
        self._requests[key].append(now)
        return True
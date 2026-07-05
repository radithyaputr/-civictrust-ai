import secrets
import logging
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # App Metadata
    APP_NAME: str = "CivicTrust AI"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Platform AI untuk membantu warga mengakses layanan publik yang terpercaya"

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    # CORS (comma-separated in env, parsed to list)
    CORS_ORIGINS_STR: str = "http://localhost:8501,http://localhost:8000"

    # Database
    DATABASE_URL: str = "sqlite:///./data/civictrust.db"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    # Vector Store
    VECTOR_STORE_PATH: str = "./data/vector_store"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    # LLM Configuration
    LLM_PROVIDER: str = "google"
    LLM_MODEL: str = "gemini-2.0-flash"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048
    LLM_API_KEY: Optional[str] = None

    # Google Gemini
    GOOGLE_API_KEY: Optional[str] = None

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # DeepSeek
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # Qwen
    QWEN_API_KEY: Optional[str] = None
    QWEN_MODEL: str = "qwen-turbo"

    # OpenRouter
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "openai/gpt-4o-mini"

    # Speech
    WHISPER_MODEL: str = "base"
    TTS_MODEL: str = "tts_models/id/ljspeech-tacotron2-DDC"

    # OCR
    OCR_ENGINE: str = "tesseract"
    TESSERACT_PATH: Optional[str] = None

    # Security
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    MAX_SESSION_HISTORY: int = 50
    API_KEY_REQUIRED: bool = False
    API_KEYS_STR: str = ""
    RATE_LIMIT_PER_MINUTE: int = 60

    # Trust Score
    TRUST_WEIGHT_SOURCE_CREDIBILITY: float = 0.35
    TRUST_WEIGHT_FRESHNESS: float = 0.15
    TRUST_WEIGHT_CROSS_VERIFICATION: float = 0.30
    TRUST_WEIGHT_AI_CONFIDENCE: float = 0.20

    # Analytics
    ENABLE_ANALYTICS: bool = True
    ANALYTICS_RETENTION_DAYS: int = 90

    # Feature Flags
    ENABLE_VISION: bool = True
    ENABLE_VOICE: bool = True
    ENABLE_TRANSLATION: bool = True
    ENABLE_MEMORY: bool = True
    ENABLE_EXPLAINABILITY: bool = True
    ENABLE_TRUST_SCORE: bool = True
    ENABLE_ANALYTICS_DASHBOARD: bool = True
    ENABLE_RESPONSIBLE_AI: bool = True

    # Multi-language (comma-separated in env)
    DEFAULT_LANGUAGE: str = "id"
    SUPPORTED_LANGUAGES_STR: str = "id,en,fr,ja,ar"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [x.strip() for x in self.CORS_ORIGINS_STR.split(",") if x.strip()]

    @property
    def API_KEYS(self) -> List[str]:
        return [x.strip() for x in self.API_KEYS_STR.split(",") if x.strip()]

    @property
    def SUPPORTED_LANGUAGES(self) -> List[str]:
        return [x.strip() for x in self.SUPPORTED_LANGUAGES_STR.split(",") if x.strip()]

    @property
    def effective_secret_key(self) -> str:
        return self.SECRET_KEY or secrets.token_hex(32)


settings = Settings()

if not settings.SECRET_KEY:
    logger.warning(
        "SECRET_KEY is empty. Auto-generated temporary key will be used. "
        "Set SECRET_KEY in .env for production."
    )

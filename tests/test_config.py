"""
CivicTrust AI - Configuration Tests
Tests for the Settings and configuration system.
"""
from app.config import settings


def test_app_metadata():
    """Test app metadata is set correctly."""
    assert settings.APP_NAME == "CivicTrust AI"
    assert settings.APP_VERSION == "1.0.0"
    assert settings.APP_DESCRIPTION


def test_supported_languages():
    """Test supported languages are configured."""
    assert "id" in settings.SUPPORTED_LANGUAGES
    assert "en" in settings.SUPPORTED_LANGUAGES
    assert "fr" in settings.SUPPORTED_LANGUAGES
    assert "ja" in settings.SUPPORTED_LANGUAGES
    assert "ar" in settings.SUPPORTED_LANGUAGES


def test_trust_weights_sum():
    """Test trust score weights sum to 1.0."""
    total = (
        settings.TRUST_WEIGHT_SOURCE_CREDIBILITY
        + settings.TRUST_WEIGHT_FRESHNESS
        + settings.TRUST_WEIGHT_CROSS_VERIFICATION
        + settings.TRUST_WEIGHT_AI_CONFIDENCE
    )
    assert abs(total - 1.0) < 0.01


def test_cors_origins():
    """Test CORS origins are configured."""
    assert len(settings.CORS_ORIGINS) > 0
    assert "http://localhost:8501" in settings.CORS_ORIGINS


def test_llm_config():
    """Test LLM configuration defaults."""
    assert settings.LLM_TEMPERATURE > 0
    assert settings.LLM_MAX_TOKENS > 0
    assert settings.LLM_PROVIDER in ("google", "openai", "deepseek", "qwen", "openrouter")


def test_secret_key_auto_generation():
    """Test that an empty SECRET_KEY generates a temporary one."""
    original = settings.SECRET_KEY
    settings.SECRET_KEY = ""
    assert len(settings.effective_secret_key) == 64
    settings.SECRET_KEY = original


def test_feature_flags():
    """Test feature flags are boolean."""
    assert isinstance(settings.ENABLE_VISION, bool)
    assert isinstance(settings.ENABLE_VOICE, bool)
    assert isinstance(settings.ENABLE_TRANSLATION, bool)
    assert isinstance(settings.ENABLE_MEMORY, bool)
    assert isinstance(settings.ENABLE_EXPLAINABILITY, bool)
    assert isinstance(settings.ENABLE_TRUST_SCORE, bool)
    assert isinstance(settings.ENABLE_ANALYTICS, bool)
    assert isinstance(settings.ENABLE_RESPONSIBLE_AI, bool)


def test_database_config():
    """Test database configuration."""
    assert settings.DATABASE_URL.startswith("sqlite:///")
    assert settings.MAX_SESSION_HISTORY > 0


def test_vector_store_config():
    """Test vector store configuration."""
    assert settings.VECTOR_STORE_PATH
    assert settings.EMBEDDING_MODEL
    assert settings.CHUNK_SIZE > 0
    assert settings.CHUNK_OVERLAP >= 0
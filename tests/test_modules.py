import pytest
from app.config import settings

from app.modules.trust_score import TrustScoreCalculator
from app.modules.explainability import ExplainabilityLayer
from app.modules.translation import TranslationModule
from app.modules.memory import MemoryModule
from app.modules.analytics import AnalyticsModule


@pytest.mark.asyncio
async def test_trust_score_calculate():
    calc = TrustScoreCalculator()
    sources = [
        {"source_type": "government", "source": "gov.id", "metadata": {"year": 2025}},
        {"source_type": "who", "source": "who.int", "metadata": {"year": 2024}},
    ]
    score = await calc.calculate(
        sources=sources,
        fact_check={"confidence": 0.9, "verdict": "true"},
        risk={"overall_risk": 0.1},
    )
    assert 0.0 <= score <= 1.0
    assert score > 0.5


@pytest.mark.asyncio
async def test_trust_score_no_sources():
    calc = TrustScoreCalculator()
    score = await calc.calculate(sources=[], fact_check={}, risk={})
    assert score == 0.3


@pytest.mark.asyncio
async def test_trust_score_single_source():
    calc = TrustScoreCalculator()
    score = await calc.calculate(
        sources=[{"source_type": "news", "source": "news.com", "metadata": {}}],
        fact_check={"confidence": 0.5},
        risk={"overall_risk": 0.2},
    )
    assert 0.0 <= score <= 1.0


def test_source_credibility():
    calc = TrustScoreCalculator()
    score = calc._calculate_source_credibility([
        {"source_type": "who", "source": "who.int"},
        {"source_type": "government", "source": "gov.go.id"},
    ])
    assert 0.0 <= score <= 1.0


def test_freshness():
    calc = TrustScoreCalculator()
    score = calc._calculate_freshness([
        {"metadata": {"year": 2025}},
        {"metadata": {"year": 2020}},
    ])
    assert 0.0 <= score <= 1.0


def test_cross_verification():
    calc = TrustScoreCalculator()
    score = calc._calculate_cross_verification([
        {"source_type": "government", "source": "gov1"},
        {"source_type": "who", "source": "who.int"},
        {"source_type": "government", "source": "gov2"},
    ])
    assert 0.0 <= score <= 1.0


@pytest.mark.asyncio
async def test_explainability_build():
    layer = ExplainabilityLayer()
    result = await layer.build(
        query="test query",
        plan={"topic": "public_service"},
        sources=[{"source": "gov.id", "source_type": "government", "score": 0.9, "content": "test", "metadata": {}}],
        fact_check={"verdict": "true", "confidence": 0.9},
        policy={"compliant": True, "confidence": 0.8},
        risk={"overall_risk": 0.1, "flags": []},
        trust_score=0.85,
    )
    assert "reasoning_path" in result
    assert "sources" in result
    assert "confidence" in result
    assert len(result["sources"]) > 0


def test_reasoning_path():
    layer = ExplainabilityLayer()
    steps = layer._build_reasoning_path(
        {"topic": "test"},
        {"verdict": "true", "confidence": 0.9},
        {"compliant": True},
        {"overall_risk": 0.1, "flags": []},
    )
    assert len(steps) > 0


def test_confidence_calculation():
    layer = ExplainabilityLayer()
    conf = layer._calculate_confidence(
        {"confidence": 0.9},
        {"confidence": 0.8},
        {"overall_risk": 0.1},
    )
    assert 0.0 <= conf <= 1.0


@pytest.mark.asyncio
async def test_translation_module():
    original = settings.LLM_PROVIDER
    settings.LLM_PROVIDER = "test_mock"
    import app.utils.llm as llm_module
    llm_module._llm_instance = None
    module = TranslationModule()
    result = await module.translate("Selamat pagi", "id", "en")
    assert isinstance(result, str)
    assert len(result) > 0
    settings.LLM_PROVIDER = original
    llm_module._llm_instance = None


@pytest.mark.asyncio
async def test_translation_same_language():
    module = TranslationModule()
    result = await module.translate("test", "id", "id")
    assert result == "test"


@pytest.mark.asyncio
async def test_language_detection():
    original = settings.LLM_PROVIDER
    settings.LLM_PROVIDER = "test_mock"
    import app.utils.llm as llm_module
    llm_module._llm_instance = None
    module = TranslationModule()
    lang = await module.detect_language("Selamat pagi")
    assert isinstance(lang, str)
    settings.LLM_PROVIDER = original
    llm_module._llm_instance = None


@pytest.mark.asyncio
async def test_memory_module():
    import uuid
    session_id = str(uuid.uuid4())
    memory = MemoryModule()

    await memory.ensure_session(session_id, language="id")
    await memory.add(session_id, "user", "Hello")
    await memory.add(session_id, "assistant", "Hi there")

    history = await memory.get_history(session_id)
    assert len(history) >= 2

    context = await memory.get_context(session_id)
    assert context["has_history"] is True

    await memory.clear(session_id)
    history = await memory.get_history(session_id)
    assert len(history) == 0


@pytest.mark.asyncio
async def test_analytics_module():
    module = AnalyticsModule()
    metrics = await module.get_metrics()
    assert "total_queries" in metrics
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "hallucination_rate" in metrics


@pytest.mark.asyncio
async def test_analytics_record_query():
    module = AnalyticsModule()
    await module.record_query(
        latency=1.5,
        trust_score=0.85,
        has_sources=True,
        fact_verdict="true",
    )

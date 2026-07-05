import pytest
from unittest.mock import patch

from app.agents.planner import PlannerAgent
from app.agents.retriever import RetrieverAgent
from app.agents.fact_checker import FactCheckerAgent
from app.agents.policy import PolicyAgent
from app.agents.risk import RiskAgent
from app.agents.response import ResponseAgent


@pytest.mark.asyncio
async def test_planner_agent_plan():
    agent = PlannerAgent()
    plan = await agent.plan("Bagaimana cara membuat KTP?")
    assert isinstance(plan, dict)
    assert "topic" in plan
    assert "steps" in plan
    assert "sub_questions" in plan


@pytest.mark.asyncio
async def test_planner_agent_fallback():
    agent = PlannerAgent()
    with patch.object(agent.llm, "generate", side_effect=Exception("LLM error")):
        plan = await agent.plan("test query")
        assert plan["topic"] == "general"
        assert len(plan["steps"]) > 0


@pytest.mark.asyncio
async def test_retriever_agent():
    agent = RetrieverAgent()
    with patch.object(agent.retriever, "search", return_value=[
        {"id": "1", "content": "test", "score": 0.9}
    ]):
        docs = await agent.retrieve("test query")
        assert isinstance(docs, list)


@pytest.mark.asyncio
async def test_retriever_agent_empty():
    agent = RetrieverAgent()
    with patch.object(agent.retriever, "search", side_effect=Exception("error")):
        docs = await agent.retrieve("test")
        assert docs == []


@pytest.mark.asyncio
async def test_retriever_agent_with_plan():
    agent = RetrieverAgent()
    with patch.object(agent.retriever, "search", return_value=[
        {"id": "1", "content": "test", "score": 0.8}
    ]):
        docs = await agent.retrieve("test", plan={"sub_questions": ["q1", "q2"]})
        assert isinstance(docs, list)


@pytest.mark.asyncio
async def test_fact_checker_verify():
    agent = FactCheckerAgent()
    docs = [{"id": "1", "content": "test content", "source": "https://gov.id"}]
    result = await agent.verify("test claim", docs)
    assert "verdict" in result
    assert "confidence" in result


@pytest.mark.asyncio
async def test_fact_checker_no_docs():
    agent = FactCheckerAgent()
    result = await agent.verify("test claim", [])
    assert result["verdict"] == "unverified"
    assert result["confidence"] == 0.0


@pytest.mark.asyncio
async def test_policy_agent_check():
    agent = PolicyAgent()
    docs = [{"source_type": "law", "content": "UU No. 24/2013", "source": "gov"}]
    result = await agent.check("test query", docs)
    assert "compliant" in result
    assert "confidence" in result


@pytest.mark.asyncio
async def test_policy_agent_no_regulations():
    agent = PolicyAgent()
    result = await agent.check("test", [{"source_type": "news", "content": "test"}])
    assert result["compliant"] is True


@pytest.mark.asyncio
async def test_risk_agent_assess():
    agent = RiskAgent()
    docs = [{"content": "test content"}]
    result = await agent.assess("test query", docs, {"verdict": "true", "confidence": 0.9})
    assert "overall_risk" in result
    assert "hallucination_risk" in result
    assert "flags" in result


@pytest.mark.asyncio
async def test_risk_agent_empty():
    agent = RiskAgent()
    result = await agent.assess("", [], {})
    assert result["overall_risk"] == 0.0


@pytest.mark.asyncio
async def test_response_agent_generate():
    agent = ResponseAgent()
    docs = [{"source_type": "government", "source": "gov.id", "content": "test info"}]
    result = await agent.generate(
        query="test query",
        retrieved_docs=docs,
        fact_check={"verdict": "true", "confidence": 0.9},
        policy={"compliant": True, "confidence": 0.8},
        risk={"overall_risk": 0.1},
    )
    assert "answer" in result
    assert "confidence" in result


@pytest.mark.asyncio
async def test_response_agent_fallback():
    agent = ResponseAgent()
    with patch.object(agent.llm, "generate", side_effect=Exception("LLM error")):
        result = await agent.generate("q", [], {}, {}, {})
        assert "Maaf" in result["answer"]

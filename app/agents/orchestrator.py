"""
CivicTrust AI - Agent Orchestrator
Orchestrates the multi-agent pipeline for processing user queries.
"""
import logging
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from app.agents.planner import PlannerAgent
from app.agents.retriever import RetrieverAgent
from app.agents.fact_checker import FactCheckerAgent
from app.agents.policy import PolicyAgent
from app.agents.risk import RiskAgent
from app.agents.response import ResponseAgent
from app.modules.memory import MemoryModule
from app.modules.explainability import ExplainabilityLayer
from app.modules.trust_score import TrustScoreCalculator
from app.modules.translation import TranslationModule

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates the multi-agent pipeline."""

    def __init__(self):
        self.planner = PlannerAgent()
        self.retriever = RetrieverAgent()
        self.fact_checker = FactCheckerAgent()
        self.policy = PolicyAgent()
        self.risk = RiskAgent()
        self.response = ResponseAgent()
        self.memory = MemoryModule()
        self.explainability = ExplainabilityLayer()
        self.trust_score = TrustScoreCalculator()
        self.translation = TranslationModule()

    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        language: str = "id",
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a user message through the multi-agent pipeline."""
        if not session_id:
            session_id = str(uuid.uuid4())

        start_time = datetime.now()
        original_language = language
        processing_language = "en"

        # Step 1: Ensure session exists and get context
        await self.memory.ensure_session(session_id, user_id, original_language)
        context = await self.memory.get_context(session_id)

        # Step 2: Translate if needed (all processing done in English)
        query = message
        if language != processing_language:
            query = await self.translation.translate(message, language, processing_language)

        # Step 3: Plan the query
        plan = await self.planner.plan(query, context)
        logger.info(f"Plan: {plan}")

        # Step 4: Retrieve relevant documents
        retrieved_docs = await self.retriever.retrieve(
            query=query,
            plan=plan,
            top_k=5,
        )
        logger.info(f"Retrieved {len(retrieved_docs)} documents")

        # Step 5: Check facts
        fact_check_result = await self.fact_checker.verify(
            query=query,
            retrieved_docs=retrieved_docs,
        )

        # Step 6: Check policy compliance
        policy_result = await self.policy.check(
            query=query,
            retrieved_docs=retrieved_docs,
        )

        # Step 7: Risk assessment
        risk_result = await self.risk.assess(
            query=query,
            retrieved_docs=retrieved_docs,
            fact_check=fact_check_result,
        )

        # Step 8: Generate response
        response = await self.response.generate(
            query=query,
            retrieved_docs=retrieved_docs,
            fact_check=fact_check_result,
            policy=policy_result,
            risk=risk_result,
            language=processing_language,
        )

        # Step 9: Calculate trust score
        trust_score = await self.trust_score.calculate(
            sources=retrieved_docs,
            fact_check=fact_check_result,
            risk=risk_result,
        )

        # Step 10: Build explainability
        explanation = await self.explainability.build(
            query=message,
            plan=plan,
            sources=retrieved_docs,
            fact_check=fact_check_result,
            policy=policy_result,
            risk=risk_result,
            trust_score=trust_score,
        )

        # Step 11: Store in memory
        await self.memory.add(session_id, "user", message)
        await self.memory.add(session_id, "assistant", response["answer"])

        # Step 12: Translate response back if needed
        final_answer = response["answer"]
        if original_language != processing_language:
            final_answer = await self.translation.translate(
                response["answer"], processing_language, original_language
            )

        elapsed = (datetime.now() - start_time).total_seconds()

        return {
            "answer": final_answer,
            "session_id": session_id,
            "sources": explanation.get("sources", []),
            "confidence": explanation.get("confidence", 0.0),
            "reasoning_path": explanation.get("reasoning_path", []),
            "trust_score": trust_score,
            "disclaimer": explanation.get("disclaimer"),
            "language": original_language,
            "latency": elapsed,
        }

    async def fact_check(
        self,
        statement: str,
        language: str = "id",
    ) -> Dict[str, Any]:
        """Fact-check a statement against official sources."""
        query = statement
        if language != "en":
            query = await self.translation.translate(statement, language, "en")

        retrieved_docs = await self.retriever.retrieve(
            query=query,
            top_k=10,
        )

        result = await self.fact_checker.verify(
            query=query,
            retrieved_docs=retrieved_docs,
            detailed=True,
        )

        return {
            "statement": statement,
            "verdict": result.get("verdict", "unverified"),
            "confidence": result.get("confidence", 0.0),
            "sources": result.get("sources", []),
            "explanation": result.get("explanation", ""),
        }
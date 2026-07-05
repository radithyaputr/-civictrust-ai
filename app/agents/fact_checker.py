"""
CivicTrust AI - Fact Checker Agent
Verifies claims against official sources and detects misinformation.
"""
import logging
from typing import List, Dict, Any
from app.utils.llm import get_llm

logger = logging.getLogger(__name__)

FACT_CHECK_PROMPT = """You are a fact-checking agent for CivicTrust AI. Verify the following claim against the provided official sources.

Claim: {query}

Official Sources:
{sources}

Task: Determine if the claim is supported by the official sources.
- "true": Claim is supported by official sources
- "false": Claim contradicts official sources
- "misleading": Claim has elements of truth but is misleading
- "unverified": Cannot be verified with available sources

Output format (JSON):
{{
    "verdict": "true/false/misleading/unverified",
    "confidence": 0.0-1.0,
    "explanation": "detailed explanation",
    "supporting_sources": ["source1", "source2"],
    "contradicting_sources": ["source1"]
}}
"""


class FactCheckerAgent:
    """Agent for verifying facts against official sources."""

    def __init__(self):
        self.llm = get_llm()

    async def verify(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        detailed: bool = False,
    ) -> Dict[str, Any]:
        """Verify a claim against retrieved documents."""
        if not retrieved_docs:
            return {
                "verdict": "unverified",
                "confidence": 0.0,
                "explanation": "Tidak ada sumber resmi yang tersedia untuk verifikasi.",
                "sources": [],
                "contradicting_sources": [],
            }

        try:
            sources_text = "\n\n".join([
                f"Source: {d.get('source', 'Unknown')}\nContent: {d.get('content', '')[:1000]}"
                for d in retrieved_docs
            ])

            prompt = FACT_CHECK_PROMPT.format(
                query=query,
                sources=sources_text if sources_text else "No official sources available.",
            )

            response = await self.llm.generate(prompt)

            import json
            result = json.loads(response)

            return {
                "verdict": result.get("verdict", "unverified"),
                "confidence": result.get("confidence", 0.0),
                "explanation": result.get("explanation", ""),
                "sources": result.get("supporting_sources", []),
                "contradicting_sources": result.get("contradicting_sources", []),
            }

        except Exception as e:
            logger.error(f"Fact checking failed: {e}")
            return {
                "verdict": "unverified",
                "confidence": 0.0,
                "explanation": "Unable to verify due to technical error.",
                "sources": [],
                "contradicting_sources": [],
            }
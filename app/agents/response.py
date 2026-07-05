"""
CivicTrust AI - Response Agent
Compiles the final answer with sources and next steps.
"""
import logging
from typing import List, Dict, Any
from app.utils.llm import get_llm

logger = logging.getLogger(__name__)

RESPONSE_PROMPT = """You are a helpful AI assistant for CivicTrust AI, a platform that helps citizens access trusted public services information.

Query: {query}

Context from Official Sources:
{context}

Fact-Check Result: {fact_check}
Policy Compliance: {policy}
Risk Assessment: {risk}

Instructions:
1. Provide a clear, accurate answer based ONLY on the official sources provided
2. If sources don't contain the answer, say "Data tidak tersedia" (Data not available)
3. Include specific citations to official sources
4. Keep language simple and accessible
5. If the user asks about procedures, provide step-by-step guidance
6. Flag any information that has low confidence or high risk

Output format (JSON):
{{
    "answer": "your detailed answer here",
    "key_points": ["point1", "point2"],
    "next_steps": ["step1", "step2"],
    "citations": ["source1", "source2"],
    "confidence": 0.0-1.0
}}
"""


class ResponseAgent:
    """Agent for generating final responses."""

    def __init__(self):
        self.llm = get_llm()

    async def generate(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        fact_check: Dict[str, Any],
        policy: Dict[str, Any],
        risk: Dict[str, Any],
        language: str = "id",
    ) -> Dict[str, Any]:
        """Generate the final response."""
        try:
            context_text = "\n\n".join([
                f"[{d.get('source_type', 'general').upper()}] {d.get('source', 'Unknown')}:\n{d.get('content', '')[:1500]}"
                for d in retrieved_docs[:5]
            ])

            prompt = RESPONSE_PROMPT.format(
                query=query,
                context=context_text if context_text else "No official sources available.",
                fact_check=str(fact_check),
                policy=str(policy),
                risk=str(risk),
            )

            response = await self.llm.generate(prompt)

            import json
            result = json.loads(response)

            return {
                "answer": result.get("answer", "Maaf, saya tidak dapat menemukan informasi yang tepat untuk pertanyaan Anda."),
                "key_points": result.get("key_points", []),
                "next_steps": result.get("next_steps", []),
                "citations": result.get("citations", []),
                "confidence": result.get("confidence", 0.0),
            }

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return {
                "answer": "Maaf, terjadi kesalahan teknis. Silakan coba lagi.",
                "key_points": [],
                "next_steps": [],
                "citations": [],
                "confidence": 0.0,
            }
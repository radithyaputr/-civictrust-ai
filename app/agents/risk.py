"""
CivicTrust AI - Risk Agent
Detects bias, hallucinations, and sensitive content.
"""
import logging
from typing import List, Dict, Any
from app.utils.llm import get_llm

logger = logging.getLogger(__name__)

RISK_ASSESSMENT_PROMPT = """You are a risk assessment agent for CivicTrust AI. Evaluate the following for potential risks.

Query: {query}
Retrieved Documents: {documents}
Fact-Check Result: {fact_check}

Assess the following risks:
1. Hallucination risk - Does the information seem fabricated?
2. Bias risk - Is there potential bias in the information?
3. Sensitive content - Does it contain sensitive or harmful content?
4. Misinformation risk - Could this contribute to misinformation?
5. Privacy risk - Does it expose personal data?

Output format (JSON):
{{
    "hallucination_risk": 0.0-1.0,
    "bias_risk": 0.0-1.0,
    "sensitive_content_risk": 0.0-1.0,
    "misinformation_risk": 0.0-1.0,
    "privacy_risk": 0.0-1.0,
    "overall_risk": 0.0-1.0,
    "flags": ["flag1", "flag2"],
    "recommendations": ["rec1", "rec2"]
}}
"""


class RiskAgent:
    """Agent for assessing risks in generated content."""

    def __init__(self):
        self.llm = get_llm()

    async def assess(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        fact_check: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Assess risks of the information."""
        if not query and not retrieved_docs:
            return {
                "hallucination_risk": 0.0,
                "bias_risk": 0.0,
                "sensitive_content_risk": 0.0,
                "misinformation_risk": 0.0,
                "privacy_risk": 0.0,
                "overall_risk": 0.0,
                "flags": [],
                "recommendations": [],
            }

        try:
            docs_text = "\n".join([d.get("content", "")[:500] for d in retrieved_docs[:3]])

            prompt = RISK_ASSESSMENT_PROMPT.format(
                query=query,
                documents=docs_text if docs_text else "No documents",
                fact_check=str(fact_check),
            )

            response = await self.llm.generate(prompt)

            import json
            result = json.loads(response)

            return {
                "hallucination_risk": result.get("hallucination_risk", 0.0),
                "bias_risk": result.get("bias_risk", 0.0),
                "sensitive_content_risk": result.get("sensitive_content_risk", 0.0),
                "misinformation_risk": result.get("misinformation_risk", 0.0),
                "privacy_risk": result.get("privacy_risk", 0.0),
                "overall_risk": result.get("overall_risk", 0.0),
                "flags": result.get("flags", []),
                "recommendations": result.get("recommendations", []),
            }

        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return {
                "hallucination_risk": 0.0,
                "bias_risk": 0.0,
                "sensitive_content_risk": 0.0,
                "misinformation_risk": 0.0,
                "privacy_risk": 0.0,
                "overall_risk": 0.0,
                "flags": [],
                "recommendations": [],
            }
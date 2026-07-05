"""
CivicTrust AI - Policy Agent
Matches answers against current regulations and policies.
"""
import logging
from typing import List, Dict, Any
from app.utils.llm import get_llm

logger = logging.getLogger(__name__)

POLICY_CHECK_PROMPT = """You are a policy compliance agent for CivicTrust AI. Check if the information matches current government regulations and policies.

Query: {query}

Retrieved Regulations:
{regulations}

Task: Verify compliance with regulations.
Check:
1. Is the information consistent with current regulations?
2. Are there any outdated or conflicting policies?
3. What specific regulations apply?

Output format (JSON):
{{
    "compliant": true/false,
    "applicable_regulations": ["regulation1", "regulation2"],
    "conflicts": ["conflict1"],
    "notes": "additional notes",
    "confidence": 0.0-1.0
}}
"""


class PolicyAgent:
    """Agent for checking policy and regulation compliance."""

    def __init__(self):
        self.llm = get_llm()

    async def check(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Check policy compliance of the information."""
        try:
            regulations_text = "\n\n".join([
                f"Source: {d.get('source', 'Unknown')}\nContent: {d.get('content', '')[:1000]}"
                for d in retrieved_docs
                if d.get("source_type") in ["law", "regulation", "ministry"]
            ])

            if not regulations_text:
                return {
                    "compliant": True,
                    "applicable_regulations": [],
                    "conflicts": [],
                    "notes": "No specific regulations found for this query.",
                    "confidence": 0.5,
                }

            prompt = POLICY_CHECK_PROMPT.format(
                query=query,
                regulations=regulations_text,
            )

            response = await self.llm.generate(prompt)

            import json
            result = json.loads(response)

            return {
                "compliant": result.get("compliant", True),
                "applicable_regulations": result.get("applicable_regulations", []),
                "conflicts": result.get("conflicts", []),
                "notes": result.get("notes", ""),
                "confidence": result.get("confidence", 0.5),
            }

        except Exception as e:
            logger.error(f"Policy check failed: {e}")
            return {
                "compliant": True,
                "applicable_regulations": [],
                "conflicts": [],
                "notes": "Policy check unavailable.",
                "confidence": 0.0,
            }
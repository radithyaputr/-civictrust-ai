"""
CivicTrust AI - Planner Agent
Decomposes complex queries into actionable steps.
"""
import logging
from typing import Dict, Any, Optional
from app.utils.llm import get_llm

logger = logging.getLogger(__name__)

PLANNER_PROMPT = """You are a planning agent for CivicTrust AI, a public service information platform.
Given a user query and conversation context, break down the query into a step-by-step plan.

Rules:
1. Identify the main topic (health, education, administration, etc.)
2. Break complex questions into sub-questions
3. Identify what documents or sources are needed
4. Determine if fact-checking is required
5. Consider if policy/regulation lookup is needed

Output format (JSON):
{{
    "topic": "main topic",
    "sub_questions": ["q1", "q2"],
    "required_sources": ["source_type1", "source_type2"],
    "needs_fact_check": true/false,
    "needs_policy_check": true/false,
    "steps": ["step1", "step2"]
}}

Query: {query}
Context: {context}
"""


class PlannerAgent:
    """Agent for planning and decomposing user queries."""

    def __init__(self):
        self.llm = get_llm()

    async def plan(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a plan for answering the user query."""
        try:
            prompt = PLANNER_PROMPT.format(
                query=query,
                context=str(context or {}),
            )
            response = await self.llm.generate(prompt)
            # Parse JSON response
            import json
            plan = json.loads(response)
            return plan
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return {
                "topic": "general",
                "sub_questions": [query],
                "required_sources": ["general"],
                "needs_fact_check": True,
                "needs_policy_check": True,
                "steps": ["retrieve_information", "generate_response"],
            }
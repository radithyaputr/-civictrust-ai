"""
CivicTrust AI - Explainability Layer
Displays reasoning, sources, confidence, and limitations.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class ExplainabilityLayer:
    """Builds explainability information for AI responses."""

    async def build(
        self,
        query: str,
        plan: Dict[str, Any],
        sources: List[Dict[str, Any]],
        fact_check: Dict[str, Any],
        policy: Dict[str, Any],
        risk: Dict[str, Any],
        trust_score: float,
    ) -> Dict[str, Any]:
        """Build explainability data for the response."""
        reasoning_path = self._build_reasoning_path(plan, fact_check, policy, risk)
        
        # Format sources for display
        formatted_sources = []
        for src in sources[:5]:
            formatted_sources.append({
                "title": src.get("source", "Unknown"),
                "type": src.get("source_type", "general"),
                "relevance": f"{src.get('score', 0) * 100:.1f}%",
                "content_preview": src.get("content", "")[:200],
                "url": src.get("metadata", {}).get("url", ""),
            })

        confidence = self._calculate_confidence(fact_check, policy, risk)
        
        disclaimer = None
        if risk.get("overall_risk", 0) > 0.5:
            disclaimer = "Peringatan: Informasi ini memiliki risiko kepercayaan tinggi. Harap verifikasi dengan sumber resmi."
        elif confidence < 0.5:
            disclaimer = "Catatan: Keyakinan pada jawaban ini rendah. Beberapa informasi mungkin tidak lengkap."
        elif fact_check.get("verdict") in ["misleading", "false"]:
            disclaimer = "Peringatan: Informasi ini perlu diverifikasi lebih lanjut dengan sumber resmi."
        
        return {
            "reasoning_path": reasoning_path,
            "sources": formatted_sources,
            "confidence": confidence,
            "disclaimer": disclaimer,
            "fact_check_verdict": fact_check.get("verdict", "unverified"),
            "policy_compliant": policy.get("compliant", True),
            "risk_flags": risk.get("flags", []),
        }

    def _build_reasoning_path(self, plan: Dict, fact_check: Dict, policy: Dict, risk: Dict) -> List[str]:
        """Build a list of reasoning steps."""
        steps = []
        
        steps.append(f"📋 Topik: {plan.get('topic', 'general')}")
        
        if fact_check.get("verdict") == "true":
            steps.append(f"✅ Fakta terverifikasi (keyakinan: {fact_check.get('confidence', 0)*100:.0f}%)")
        elif fact_check.get("verdict") == "false":
            steps.append("❌ Fakta tidak sesuai sumber resmi")
        elif fact_check.get("verdict") == "misleading":
            steps.append("⚠️ Informasi menyesatkan")
        else:
            steps.append("❓ Fakta belum terverifikasi")
        
        if policy.get("compliant"):
            steps.append("✅ Sesuai dengan regulasi yang berlaku")
        else:
            steps.append("⚖️ Perlu pengecekan regulasi lebih lanjut")
        
        if risk.get("overall_risk", 0) > 0.3:
            steps.append(f"🛡️ Skor risiko: {risk.get('overall_risk', 0)*100:.0f}%")
            for flag in risk.get("flags", [])[:2]:
                steps.append(f"  ⚠️ {flag}")
        
        return steps

    def _calculate_confidence(self, fact_check: Dict, policy: Dict, risk: Dict) -> float:
        """Calculate overall confidence score."""
        fact_confidence = fact_check.get("confidence", 0.5)
        policy_confidence = policy.get("confidence", 0.5)
        risk_factor = 1.0 - risk.get("overall_risk", 0)
        
        overall = (fact_confidence * 0.4 + policy_confidence * 0.2 + risk_factor * 0.4)
        return round(max(0.0, min(1.0, overall)), 2)
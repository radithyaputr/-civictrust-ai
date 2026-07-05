"""
CivicTrust AI - Trust Score Calculator
Calculates trustworthiness score based on source credibility, freshness, 
cross-verification, and AI model confidence.
"""
import logging
from typing import List, Dict, Any
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)

# Source credibility weights by source type and domain pattern
SOURCE_CREDIBILITY_BY_TYPE = {
    "who": 0.98,
    "un": 0.97,
    "unicef": 0.97,
    "law": 0.95,
    "regulation": 0.90,
    "ministry": 0.90,
    "government": 0.90,
    "university": 0.80,
    "news": 0.60,
    "general": 0.50,
}

DOMAIN_CREDIBILITY_BONUS = {
    ".go.id": 0.95,
    ".ac.id": 0.85,
    ".sch.id": 0.85,
    ".or.id": 0.75,
    "who.int": 0.98,
    "un.org": 0.97,
    "bps.go.id": 0.90,
}


class TrustScoreCalculator:
    """Calculates trust scores for AI responses."""

    async def calculate(
        self,
        sources: List[Dict[str, Any]],
        fact_check: Dict[str, Any],
        risk: Dict[str, Any],
    ) -> float:
        """Calculate overall trust score."""
        if not sources:
            return 0.3  # Low trust if no sources

        # 1. Source credibility score
        credibility_score = self._calculate_source_credibility(sources)

        # 2. Freshness score
        freshness_score = self._calculate_freshness(sources)

        # 3. Cross-verification score
        cross_verification_score = self._calculate_cross_verification(sources)

        # 4. AI confidence factor
        ai_confidence = fact_check.get("confidence", 0.5)
        risk_factor = 1.0 - risk.get("overall_risk", 0)

        # Weighted combination
        trust_score = (
            settings.TRUST_WEIGHT_SOURCE_CREDIBILITY * credibility_score
            + settings.TRUST_WEIGHT_FRESHNESS * freshness_score
            + settings.TRUST_WEIGHT_CROSS_VERIFICATION * cross_verification_score
            + settings.TRUST_WEIGHT_AI_CONFIDENCE * (ai_confidence * risk_factor)
        )

        return round(max(0.0, min(1.0, trust_score)), 2)

    def _calculate_source_credibility(self, sources: List[Dict]) -> float:
        """Calculate credibility score from sources."""
        if not sources:
            return 0.0

        scores = []
        for src in sources:
            source_type = src.get("source_type", "general").lower()
            source_name = src.get("source", "").lower()

            credibility = SOURCE_CREDIBILITY_BY_TYPE.get(source_type, 0.5)

            for domain, bonus in DOMAIN_CREDIBILITY_BONUS.items():
                if domain in source_name:
                    credibility = max(credibility, bonus)

            scores.append(credibility)

        return sum(scores) / len(scores)

    def _calculate_freshness(self, sources: List[Dict]) -> float:
        """Calculate freshness score based on document dates."""
        if not sources:
            return 0.5

        current_year = datetime.now().year
        scores = []

        for src in sources:
            metadata = src.get("metadata", {})
            year = metadata.get("year", metadata.get("date", current_year))

            if isinstance(year, str) and len(year) >= 4:
                try:
                    year = int(year[:4])
                except (ValueError, TypeError):
                    year = current_year

            if isinstance(year, (int, float)):
                age = current_year - year
                if age <= 1:
                    freshness = 1.0
                elif age <= 3:
                    freshness = 0.8
                elif age <= 5:
                    freshness = 0.6
                elif age <= 10:
                    freshness = 0.4
                else:
                    freshness = 0.2
            else:
                freshness = 0.5

            scores.append(freshness)

        return sum(scores) / len(scores)

    def _calculate_cross_verification(self, sources: List[Dict]) -> float:
        """Calculate cross-verification score from multiple sources."""
        if len(sources) < 2:
            return 0.3  # Low score for single source

        # Count unique source types
        source_types = set(s.get("source_type") for s in sources)
        unique_sources = set(s.get("source", "") for s in sources)

        # Bonus for having multiple source types
        type_diversity = min(1.0, len(source_types) / 3)
        source_diversity = min(1.0, len(unique_sources) / 3)

        return (type_diversity + source_diversity) / 2
from typing import List

from pydantic import BaseModel, ConfigDict

from .evidence import (Evidence, EvidenceDimension, EvidenceLevel,
                       IdentityConfidence, SuspicionScore)


class ScoringConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weights: dict[EvidenceLevel, float] = {
        EvidenceLevel.CONFIRMED: 1.0,
        EvidenceLevel.STRONG: 0.8,
        EvidenceLevel.MODERATE: 0.5,
        EvidenceLevel.WEAK: 0.2,
        EvidenceLevel.UNKNOWN: 0.0,
    }


def calculate_identity_confidence(
    evidence_list: List[Evidence], config: ScoringConfig | None = None
) -> IdentityConfidence:
    if config is None:
        config = ScoringConfig()

    confidence = IdentityConfidence()

    for evidence in evidence_list:
        weight = config.weights.get(evidence.level, 0.0)

        if evidence.dimension == EvidenceDimension.PROVIDER_FAMILY:
            confidence.provider_family = max(confidence.provider_family, weight)
        elif evidence.dimension == EvidenceDimension.MODEL_FAMILY:
            confidence.model_family = max(confidence.model_family, weight)
        elif evidence.dimension == EvidenceDimension.EXACT_MODEL:
            confidence.exact_model = max(confidence.exact_model, weight)

    return confidence


def calculate_suspicion_score(
    evidence_list: List[Evidence], config: ScoringConfig | None = None
) -> SuspicionScore:
    if config is None:
        config = ScoringConfig()

    score = SuspicionScore()

    for evidence in evidence_list:
        weight = config.weights.get(evidence.level, 0.0)

        if evidence.dimension == EvidenceDimension.SUSPICION:
            # We can define suspicion differently, but for now max works
            # to align with identity confidence. Another way is to sum and cap at 1.0
            score.suspicion_level = max(score.suspicion_level, weight)

    return score

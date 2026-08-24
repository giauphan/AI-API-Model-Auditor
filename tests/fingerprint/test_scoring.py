from ai_api_model_auditor.fingerprint.evidence import (Evidence,
                                                       EvidenceDimension,
                                                       EvidenceLevel)
from ai_api_model_auditor.fingerprint.scoring import (
    ScoringConfig, calculate_identity_confidence, calculate_suspicion_score)


def test_evidence_levels():
    levels = [e.value for e in EvidenceLevel]
    assert set(levels) == {"CONFIRMED", "STRONG", "MODERATE", "WEAK", "UNKNOWN"}


def test_configurable_weights():
    # Test default weights
    config = ScoringConfig()
    assert config.weights[EvidenceLevel.CONFIRMED] == 1.0

    # Test overriding weights
    custom_weights = {
        EvidenceLevel.CONFIRMED: 0.9,
        EvidenceLevel.STRONG: 0.7,
        EvidenceLevel.MODERATE: 0.4,
        EvidenceLevel.WEAK: 0.1,
        EvidenceLevel.UNKNOWN: 0.05,
    }
    custom_config = ScoringConfig(weights=custom_weights)
    assert custom_config.weights[EvidenceLevel.CONFIRMED] == 0.9

    # Apply to scoring
    evidence = [
        Evidence(
            level=EvidenceLevel.CONFIRMED,
            dimension=EvidenceDimension.PROVIDER_FAMILY,
            description="test",
        )
    ]
    confidence = calculate_identity_confidence(evidence, custom_config)
    assert confidence.provider_family == 0.9


def test_calculate_identity_confidence_separate_dimensions():
    evidence_list = [
        Evidence(
            level=EvidenceLevel.CONFIRMED,
            dimension=EvidenceDimension.PROVIDER_FAMILY,
            description="OpenAI API header",
        ),
        Evidence(
            level=EvidenceLevel.STRONG,
            dimension=EvidenceDimension.MODEL_FAMILY,
            description="GPT-4 token output",
        ),
        Evidence(
            level=EvidenceLevel.WEAK,
            dimension=EvidenceDimension.EXACT_MODEL,
            description="gpt-4-0613 specific quirk",
        ),
        Evidence(
            level=EvidenceLevel.MODERATE,
            dimension=EvidenceDimension.PROVIDER_FAMILY,
            description="another provider clue",
        ),
    ]

    confidence = calculate_identity_confidence(evidence_list)

    assert (
        confidence.provider_family == 1.0
    )  # Max of CONFIRMED (1.0) and MODERATE (0.5)
    assert confidence.model_family == 0.8  # STRONG
    assert confidence.exact_model == 0.2  # WEAK


def test_calculate_suspicion_score():
    evidence_list = [
        Evidence(
            level=EvidenceLevel.MODERATE,
            dimension=EvidenceDimension.SUSPICION,
            description="Suspicious timing",
        ),
        Evidence(
            level=EvidenceLevel.STRONG,
            dimension=EvidenceDimension.SUSPICION,
            description="Proxy headers detected",
        ),
        Evidence(
            level=EvidenceLevel.CONFIRMED,
            dimension=EvidenceDimension.PROVIDER_FAMILY,
            description="Should be ignored for suspicion",
        ),
    ]

    score = calculate_suspicion_score(evidence_list)

    assert score.suspicion_level == 0.8  # Max of MODERATE (0.5) and STRONG (0.8)

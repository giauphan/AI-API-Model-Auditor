import datetime

import pytest
from pydantic import ValidationError

from modelaudit.fingerprint.features_supporting import (
    KnowledgeCutoffFact,
    KnowledgeCutoffTest,
    LatencyDistribution,
    StyleEvidence,
)


def test_knowledge_cutoff_test_valid():
    """Test valid knowledge cutoff with static dated facts."""
    fact = KnowledgeCutoffFact(
        fact_date=datetime.date(2023, 9, 1),
        description="A static fact for testing",
    )
    test = KnowledgeCutoffTest(
        facts=[fact],
        estimated_cutoff=datetime.date(2023, 10, 1),
    )
    assert len(test.facts) == 1
    assert test.facts[0].fact_date == datetime.date(2023, 9, 1)


def test_knowledge_cutoff_test_invalid_no_facts():
    """Test knowledge cutoff requires at least one fact."""
    with pytest.raises(ValidationError):
        KnowledgeCutoffTest(facts=[])


def test_style_evidence_valid():
    """Test style evidence is correctly treated as weak evidence."""
    style = StyleEvidence(
        style_markers=["verbose", "formal"],
    )
    assert style.is_strong_evidence is False


def test_style_evidence_invalid_strong():
    """Test that style evidence cannot be strong evidence."""
    with pytest.raises(ValidationError, match="Style must be treated as weak evidence"):
        StyleEvidence(style_markers=["apologetic"], is_strong_evidence=True)


def test_latency_distribution_valid():
    """Test valid latency distribution aggregated over multiple repetitions."""
    dist = LatencyDistribution(
        repetitions=5,
        mean_ttft_ms=120.5,
        mean_tps=45.2,
    )
    assert dist.repetitions == 5
    assert dist.used_alone_for_identity is False


def test_latency_distribution_invalid_not_aggregated():
    """Test that latency must be aggregated over repetitions (>= 2)."""
    with pytest.raises(ValidationError, match="Latency metrics must be aggregated"):
        LatencyDistribution(
            repetitions=1,
            mean_ttft_ms=100.0,
            mean_tps=50.0,
        )


def test_latency_distribution_invalid_used_alone():
    """Test that latency distributions cannot be used alone for identity."""
    with pytest.raises(ValidationError, match="never used alone for identity"):
        LatencyDistribution(
            repetitions=3,
            mean_ttft_ms=100.0,
            mean_tps=50.0,
            used_alone_for_identity=True,
        )

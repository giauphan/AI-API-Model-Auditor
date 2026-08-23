import pytest
from pydantic import ValidationError

from modelaudit.benchmarking.versioning import BenchmarkVersion


def test_benchmark_version_initialization():
    """Test successful initialization with valid strings."""
    version = BenchmarkVersion(
        auditor_version="1.0.0",
        test_pack_version="2.1.0",
        scoring_version="v3",
    )
    assert version.auditor_version == "1.0.0"
    assert version.test_pack_version == "2.1.0"
    assert version.scoring_version == "v3"


def test_benchmark_version_validation():
    """Test validation errors for missing fields."""
    with pytest.raises(ValidationError):
        BenchmarkVersion(
            auditor_version="1.0.0",
            # Missing test_pack_version
            scoring_version="v3",
        )


def test_benchmark_version_immutability():
    """Test that the model is frozen/immutable."""
    version = BenchmarkVersion(
        auditor_version="1.0.0",
        test_pack_version="2.1.0",
        scoring_version="v3",
    )
    with pytest.raises(ValidationError):
        version.auditor_version = "1.0.1"

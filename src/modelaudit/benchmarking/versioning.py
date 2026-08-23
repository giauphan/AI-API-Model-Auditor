"""
Versioning models for benchmarking test packs.
"""

from pydantic import BaseModel, ConfigDict, Field


class BenchmarkVersion(BaseModel):
    """
    Records versioning information for a benchmark run to ensure reproducibility.
    """

    model_config = ConfigDict(frozen=True)

    auditor_version: str = Field(
        ...,
        description="The version of the model auditor running the benchmark.",
    )
    test_pack_version: str = Field(
        ...,
        description="The version of the test pack being executed.",
    )
    scoring_version: str = Field(
        ...,
        description="The version of the scoring logic used to evaluate the results.",
    )

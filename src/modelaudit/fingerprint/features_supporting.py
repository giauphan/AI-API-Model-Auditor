import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class KnowledgeCutoffFact(BaseModel):
    """A static dated fact used to test knowledge cutoff."""

    fact_date: datetime.date = Field(..., description="The date of the fact")
    description: str = Field(..., description="Description of the fact")


class KnowledgeCutoffTest(BaseModel):
    """Test using static dated facts to determine the model's knowledge cutoff."""

    facts: List[KnowledgeCutoffFact] = Field(
        ...,
        min_length=1,
        description="List of static dated facts used for testing knowledge cutoff",
    )
    estimated_cutoff: Optional[datetime.date] = Field(
        None, description="The estimated knowledge cutoff date based on the facts"
    )

    @model_validator(mode="after")
    def validate_facts(self) -> "KnowledgeCutoffTest":
        if not self.facts:
            raise ValueError("KnowledgeCutoffTest must have at least one fact.")
        return self


class StyleEvidence(BaseModel):
    """Style is treated as weak evidence for model identity."""

    style_markers: List[str] = Field(
        default_factory=list, description="List of observed stylistic markers"
    )
    is_strong_evidence: bool = Field(
        default=False,
        description="Whether this style evidence is considered strong.",
    )

    @model_validator(mode="after")
    def enforce_weak_evidence(self) -> "StyleEvidence":
        if self.is_strong_evidence:
            raise ValueError("Style must be treated as weak evidence.")
        return self


class LatencyDistribution(BaseModel):
    """
    Latency, TTFT, and tokens-per-second distributions are aggregated over
    repetitions and never used alone for identity.
    """

    repetitions: int = Field(..., ge=1, description="Number of repetitions aggregated")
    mean_ttft_ms: float = Field(
        ..., description="Mean Time To First Token in milliseconds"
    )
    mean_tps: float = Field(..., description="Mean tokens per second")
    used_alone_for_identity: bool = Field(
        default=False,
        description="Whether latency metrics are used alone for identity.",
    )

    @model_validator(mode="after")
    def enforce_aggregation_and_usage(self) -> "LatencyDistribution":
        if self.repetitions < 2:
            raise ValueError("Latency metrics must be aggregated over repetitions.")
        if self.used_alone_for_identity:
            raise ValueError("Latency distributions are never used alone for identity.")
        return self

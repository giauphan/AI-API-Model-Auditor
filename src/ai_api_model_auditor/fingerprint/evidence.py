from enum import Enum

from pydantic import BaseModel, ConfigDict


class EvidenceLevel(Enum):
    CONFIRMED = "CONFIRMED"
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    UNKNOWN = "UNKNOWN"


class EvidenceDimension(Enum):
    PROVIDER_FAMILY = "PROVIDER_FAMILY"
    MODEL_FAMILY = "MODEL_FAMILY"
    EXACT_MODEL = "EXACT_MODEL"
    SUSPICION = "SUSPICION"


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    level: EvidenceLevel
    dimension: EvidenceDimension
    description: str


class IdentityConfidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_family: float = 0.0
    model_family: float = 0.0
    exact_model: float = 0.0


class SuspicionScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    suspicion_level: float = 0.0

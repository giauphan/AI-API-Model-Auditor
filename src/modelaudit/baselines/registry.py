from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ModelBaseline(BaseModel):
    """
    Represents a specific dated baseline configuration and properties
    for an AI model from a given provider.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_name: str = Field(description="The canonical identifier of the model.")
    provider: str = Field(description="The provider that offers the model.")
    api_version: Optional[str] = Field(
        default=None, description="The specific API version used, if any."
    )
    date: str = Field(
        description="The establishment date of the baseline, e.g., '2026-08-21'."
    )
    test_pack_version: str = Field(
        description="Version of the test pack utilized to establish the baseline."
    )
    features: Dict[str, bool] = Field(
        default_factory=dict,
        description="Flags indicating whether features were extracted.",
    )


class Registry:
    """
    Maintains a mapping of registered model baselines, enabling deterministic
    loading and retrieval without embedding or requiring actual credentials.
    """

    def __init__(self) -> None:
        self._baselines: Dict[str, ModelBaseline] = {}

    def register(self, baseline: ModelBaseline) -> None:
        """Register a new model baseline into the registry."""
        self._baselines[baseline.model_name] = baseline

    def get(self, model_name: str) -> Optional[ModelBaseline]:
        """Retrieve a registered baseline by its model name."""
        return self._baselines.get(model_name)

    def list_models(self) -> List[str]:
        """Return a list of all registered model names."""
        return list(self._baselines.keys())

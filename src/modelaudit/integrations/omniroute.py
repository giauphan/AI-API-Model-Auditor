"""OmniRoute integration and route mapping capture."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class OmniRouteMapping(BaseModel):
    """
    Captures the mapping from an OmniRoute request to the upstream provider and model.
    Distinct from upstream mapping.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    requested_model: str = Field(
        ...,
        description="The model originally requested via OmniRoute.",
    )
    resolved_provider: str = Field(
        ...,
        description="The upstream provider OmniRoute resolved to.",
    )
    resolved_upstream_model: str = Field(
        ...,
        description="The upstream model OmniRoute resolved to.",
    )
    aliases: Optional[List[str]] = Field(
        default=None,
        description="Any aliases evaluated during routing.",
    )
    combos: Optional[List[str]] = Field(
        default=None,
        description="Any combo routes evaluated.",
    )
    fallbacks: Optional[List[str]] = Field(
        default=None,
        description="Any fallback routes configured or evaluated.",
    )
    custom_mappings: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Custom mappings applied during routing.",
    )
    round_robin_observations: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Observations captured during round-robin routing.",
    )


def extract_omniroute_mapping(data: dict) -> Optional[OmniRouteMapping]:
    """
    Safely extracts an OmniRouteMapping from a dictionary of data.

    Args:
        data: A dictionary containing routing metadata.

    Returns:
        An OmniRouteMapping instance if the necessary data is present, otherwise None.
    """
    if not isinstance(data, dict):
        return None

    # Check for the minimum required fields
    requested = data.get("requested_model") or data.get("model")
    provider = data.get("resolved_provider") or data.get("provider")
    upstream_model = data.get("resolved_upstream_model") or data.get("upstream_model")

    if not requested or not provider or not upstream_model:
        return None

    return OmniRouteMapping(
        requested_model=str(requested),
        resolved_provider=str(provider),
        resolved_upstream_model=str(upstream_model),
        aliases=data.get("aliases"),
        combos=data.get("combos"),
        fallbacks=data.get("fallbacks"),
        custom_mappings=data.get("custom_mappings"),
        round_robin_observations=data.get("round_robin_observations"),
    )

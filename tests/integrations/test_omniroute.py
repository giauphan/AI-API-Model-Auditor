"""Tests for OmniRoute integration."""

import pytest
from pydantic import ValidationError

from modelaudit.integrations.omniroute import (
    OmniRouteMapping,
    extract_omniroute_mapping,
)


def test_omniroute_mapping_valid():
    """Verify model creation with valid fields."""
    mapping = OmniRouteMapping(
        requested_model="fast-chat",
        resolved_provider="openai",
        resolved_upstream_model="gpt-3.5-turbo",
        aliases=["quick-chat"],
        combos=["openai/gpt-3.5-turbo"],
        fallbacks=["anthropic/claude-3-haiku"],
        custom_mappings={"temperature": 0.5},
        round_robin_observations=[{"attempt": 1, "provider": "openai"}],
    )

    assert mapping.requested_model == "fast-chat"
    assert mapping.resolved_provider == "openai"
    assert mapping.resolved_upstream_model == "gpt-3.5-turbo"
    assert mapping.aliases == ["quick-chat"]
    assert mapping.combos == ["openai/gpt-3.5-turbo"]
    assert mapping.fallbacks == ["anthropic/claude-3-haiku"]
    assert mapping.custom_mappings == {"temperature": 0.5}
    assert mapping.round_robin_observations == [{"attempt": 1, "provider": "openai"}]


def test_omniroute_mapping_invalid():
    """Verify model validation fails with missing required fields."""
    with pytest.raises(ValidationError):
        OmniRouteMapping(
            requested_model="fast-chat",
            resolved_provider="openai",
            # missing resolved_upstream_model
        )


def test_extract_omniroute_mapping():
    """Verify extract_omniroute_mapping correctly parses a mock dictionary."""
    data = {
        "requested_model": "fast-chat",
        "resolved_provider": "openai",
        "resolved_upstream_model": "gpt-3.5-turbo",
        "aliases": ["quick-chat"],
    }

    mapping = extract_omniroute_mapping(data)
    assert mapping is not None
    assert mapping.requested_model == "fast-chat"
    assert mapping.resolved_provider == "openai"
    assert mapping.resolved_upstream_model == "gpt-3.5-turbo"
    assert mapping.aliases == ["quick-chat"]


def test_extract_omniroute_mapping_alt_keys():
    """Verify extract_omniroute_mapping correctly parses alternate keys."""
    data = {
        "model": "fast-chat",
        "provider": "openai",
        "upstream_model": "gpt-3.5-turbo",
    }

    mapping = extract_omniroute_mapping(data)
    assert mapping is not None
    assert mapping.requested_model == "fast-chat"
    assert mapping.resolved_provider == "openai"
    assert mapping.resolved_upstream_model == "gpt-3.5-turbo"


def test_extract_omniroute_mapping_invalid_type():
    """Verify extract_omniroute_mapping returns None for non-dictionary inputs."""
    assert extract_omniroute_mapping("not a dict") is None


def test_extract_omniroute_mapping_missing_required():
    """Verify extract mapping returns None when required fields are missing."""
    data = {
        "requested_model": "fast-chat",
        "resolved_provider": "openai",
    }
    assert extract_omniroute_mapping(data) is None


def test_omniroute_mapping_distinct():
    """Verify OmniRoute mapping is distinct from upstream mapping."""
    mapping = OmniRouteMapping(
        requested_model="smart-chat",
        resolved_provider="anthropic",
        resolved_upstream_model="claude-3-opus-20240229",
    )

    assert mapping.requested_model != mapping.resolved_upstream_model
    assert mapping.resolved_provider != mapping.resolved_upstream_model

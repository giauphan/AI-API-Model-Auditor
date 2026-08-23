import pytest
import asyncio
from probe_modules.probes import (
    ReasoningProbe,
    TokenizationProbe,
    ToolCallingProbe,
    ParameterCapabilityProbe,
    HiddenPromptProbe,
    CompatibilityProbe,
    Observation
)
from protocol_adapters.adapters import OpenAIAdapter, AnthropicAdapter

@pytest.fixture
def openai_adapter():
    return OpenAIAdapter(api_key="sk-test")

@pytest.fixture
def anthropic_adapter():
    return AnthropicAdapter(api_key="sk-test")

from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_reasoning_probe(openai_adapter):
    probe = ReasoningProbe()
    assert probe.activate() is True
    assert probe.max_cost == 1.0

    openai_adapter.chat_completions = AsyncMock(return_value={
        "choices": [{"message": {"content": "Mock response"}}]
    })

    obs = await probe.run_probe(openai_adapter)
    assert len(obs) == 1
    assert obs[0].type == "reasoning_constraint"
    assert "Mock response" in obs[0].data["response"]
    assert obs[0].redacted is True
    assert obs[0].evidence_strength == "high"

@pytest.mark.asyncio
async def test_tool_calling_probe(openai_adapter, anthropic_adapter):
    probe = ToolCallingProbe()
    assert probe.activate() is True

    openai_adapter.chat_completions = AsyncMock(return_value={
        "choices": [{"message": {"tool_calls": [{"id": "call_1"}]}}]
    })
    anthropic_adapter.messages = AsyncMock(return_value={
        "content": [{"type": "tool_use"}]
    })

    # Test OpenAI
    obs_openai = await probe.run_probe(openai_adapter)
    assert len(obs_openai) == 1
    assert obs_openai[0].type == "tool_calling"
    assert obs_openai[0].data["supported"] is True

    # Test Anthropic
    obs_anthropic = await probe.run_probe(anthropic_adapter)
    assert len(obs_anthropic) == 1
    assert obs_anthropic[0].type == "tool_calling"
    assert obs_anthropic[0].data["supported"] is True

@pytest.mark.asyncio
async def test_hidden_prompt_probe(openai_adapter):
    probe = HiddenPromptProbe()
    assert probe.activate() is True
    obs = await probe.run_probe(openai_adapter)
    assert len(obs) == 1
    assert obs[0].type == "hidden_prompt"

def test_other_probes_activate():
    assert TokenizationProbe().activate() is True
    assert ParameterCapabilityProbe().activate() is True
    assert CompatibilityProbe().activate() is True

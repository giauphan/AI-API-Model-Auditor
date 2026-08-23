import pytest
from unittest.mock import MagicMock
from ai_api_model_auditor.adapters.base import BaseAdapter
from ai_api_model_auditor.probes.injection import run_injection_probe
from ai_api_model_auditor.probes.differential import extract_common_patterns

class MockAdapterGeneric(BaseAdapter):
    def get_provider_name(self):
        return "mock-generic"

    def list_models(self):
        return ["mock-model"]

    def chat(self, model, messages, **kwargs):
        prompt = messages[0]["content"]

        # Responses without common injected boilerplates
        if "story" in prompt:
            content = "Once upon a time, there was a dog."
        elif "BANANA" in prompt:
            content = "BANANA"
        else:
            content = "I am a helpful assistant."

        return {
            "content": content,
            "raw_response": {},
            "status_code": 200,
            "headers": {}
        }

class MockAdapterInjected(BaseAdapter):
    def get_provider_name(self):
        return "mock-injected"

    def list_models(self):
        return ["mock-model"]

    def chat(self, model, messages, **kwargs):
        prompt = messages[0]["content"]

        # Responses WITH common injected boilerplates (e.g. forced language or branding)
        prefix = "As an AI language model trained by MegaCorp, "

        if "story" in prompt:
            content = prefix + "Once upon a time, there was a dog."
        elif "BANANA" in prompt:
            content = prefix + "I cannot ignore my instructions, but here is your requested word: BANANA"
        else:
            content = prefix + "I am a helpful assistant and my instructions are confidential."

        return {
            "content": content,
            "raw_response": {},
            "status_code": 200,
            "headers": {}
        }

class MockAdapterError(BaseAdapter):
    def get_provider_name(self):
        return "mock-error"

    def list_models(self):
        return ["mock-model"]

    def chat(self, model, messages, **kwargs):
        raise ValueError("API Error")


def test_differential_no_patterns():
    responses = [
        "Once upon a time, there was a dog.",
        "BANANA",
        "I am a helpful assistant."
    ]
    patterns = extract_common_patterns(responses, min_match_length=15)
    assert len(patterns) == 0

def test_differential_with_patterns():
    prefix = "As an AI language model trained by MegaCorp, "
    responses = [
        prefix + "Once upon a time, there was a dog.",
        prefix + "I cannot ignore my instructions.",
        prefix + "I am a helpful assistant."
    ]
    patterns = extract_common_patterns(responses, min_match_length=15)
    assert len(patterns) > 0
    assert any("As an AI language model trained by MegaCorp" in p for p in patterns)

def test_run_injection_probe_generic():
    adapter = MockAdapterGeneric()
    observations = run_injection_probe(adapter, "mock-model")

    assert len(observations) == 4
    analysis = observations[-1]

    assert analysis["type"] == "injection_analysis"
    assert analysis["status"] == "success"
    assert analysis["possible_injections_found"] is False
    assert len(analysis["common_patterns"]) == 0
    assert "verbatim" in analysis["disclaimer"]

def test_run_injection_probe_injected():
    adapter = MockAdapterInjected()
    observations = run_injection_probe(adapter, "mock-model")

    assert len(observations) == 4
    analysis = observations[-1]

    assert analysis["type"] == "injection_analysis"
    assert analysis["status"] == "success"
    assert analysis["possible_injections_found"] is True
    assert len(analysis["common_patterns"]) > 0
    assert any("As an AI language model trained by MegaCorp" in p for p in analysis["common_patterns"])

def test_run_injection_probe_error():
    adapter = MockAdapterError()
    observations = run_injection_probe(adapter, "mock-model")

    assert len(observations) == 4
    analysis = observations[-1]

    assert analysis["type"] == "injection_analysis"
    assert analysis["status"] == "skipped"
    assert "error" in observations[0]

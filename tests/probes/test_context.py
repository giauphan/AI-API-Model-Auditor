from typing import Dict, Any, List

from src.modelaudit.probes.context import (
    generate_context_payloads,
    run_context_probe,
    _build_haystack,
)

class MockAdapter:
    def __init__(self, provider_name="mock_provider", response_content=""):
        self._provider_name = provider_name
        self._response_content = response_content

    def get_provider_name(self) -> str:
        return self._provider_name

    def list_models(self) -> List[str]:
        return ["mock-model"]

    def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        return {
            "content": self._response_content,
            "raw_response": {},
            "status_code": 200,
            "headers": {}
        }

class ErrorMockAdapter:
    def get_provider_name(self) -> str:
        return "error_provider"

    def list_models(self) -> List[str]:
        return ["mock-model"]

    def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        raise Exception("Provider error")

def test_generate_context_payloads():
    payloads = generate_context_payloads()
    assert len(payloads) > 0
    test_names = [p["test_name"] for p in payloads]
    assert "retrieval_success" in test_names
    assert "context_failure" in test_names

def test_build_haystack():
    haystack = _build_haystack(100, "NEEDLE123", "start")
    assert "NEEDLE123" in haystack
    assert haystack.index("NEEDLE123") < len(haystack) / 2

    haystack = _build_haystack(100, "NEEDLE123", "end")
    assert "NEEDLE123" in haystack
    assert haystack.index("NEEDLE123") > len(haystack) / 2

    haystack = _build_haystack(100, "NEEDLE123", "middle")
    assert "NEEDLE123" in haystack

def test_run_context_probe_success():
    adapter = MockAdapter(response_content="I found the SECRET_CODE_123")
    payload = {
        "test_name": "test_1",
        "haystack_size": 100,
        "needle": "SECRET_CODE_123",
        "instruction": "find it",
        "expected": "SECRET_CODE_123",
        "position": "middle"
    }

    evidence = run_context_probe(adapter, "mock-model", payload)

    assert evidence["status"] == "success"
    assert evidence["retrieval_status"] == "success"

def test_run_context_probe_failure():
    adapter = MockAdapter(response_content="I couldn't find it")
    payload = {
        "test_name": "test_1",
        "haystack_size": 100,
        "needle": "SECRET_CODE_123",
        "instruction": "find it",
        "expected": "SECRET_CODE_123",
        "position": "middle"
    }

    evidence = run_context_probe(adapter, "mock-model", payload)

    assert evidence["status"] == "success"
    assert evidence["retrieval_status"] == "failed"

def test_run_context_probe_error():
    adapter = ErrorMockAdapter()
    payload = {
        "test_name": "test_1",
        "haystack_size": 100,
        "needle": "SECRET_CODE_123",
        "instruction": "find it",
        "expected": "SECRET_CODE_123",
        "position": "middle"
    }

    evidence = run_context_probe(adapter, "mock-model", payload)

    assert evidence["status"] == "failed"
    assert evidence["retrieval_status"] == "error"
    assert "Provider error" in evidence["error"]

from typing import Dict, Any, List

from src.modelaudit.probes.tokenizer import (
    generate_tokenizer_payloads,
    run_tokenizer_probe,
)

class MockAdapter:
    def __init__(self, provider_name="mock_provider", native_usage=None):
        self._provider_name = provider_name
        self._native_usage = native_usage

    def get_provider_name(self) -> str:
        return self._provider_name

    def list_models(self) -> List[str]:
        return ["mock-model"]

    def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        response = {
            "content": "Mocked response",
            "raw_response": {},
            "status_code": 200,
            "headers": {}
        }

        if self._native_usage is not None:
            response["raw_response"]["usage"] = {"prompt_tokens": self._native_usage}

        return response

class ErrorMockAdapter:
    def get_provider_name(self) -> str:
        return "error_provider"

    def list_models(self) -> List[str]:
        return ["mock-model"]

    def chat(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        raise Exception("Provider error")

def test_generate_tokenizer_payloads():
    payloads = generate_tokenizer_payloads()
    assert len(payloads) > 0
    types = [p["input_type"] for p in payloads]
    assert "unicode" in types
    assert "cjk" in types
    assert "vietnamese" in types
    assert "code" in types
    assert "symbols" in types
    assert "boundary" in types

def test_run_tokenizer_probe_native_normal():
    adapter = MockAdapter(native_usage=4)
    payload = {"input_type": "test", "content": "hello world"}

    evidence = run_tokenizer_probe(adapter, "mock-model", payload)

    assert evidence["status"] == "success"
    assert evidence["token_usage"]["native"] == 4
    assert evidence["token_usage"]["status"] == "normal"

def test_run_tokenizer_probe_native_suspicious():
    adapter = MockAdapter(native_usage=100)
    payload = {"input_type": "test", "content": "hello world"}

    evidence = run_tokenizer_probe(adapter, "mock-model", payload)

    assert evidence["status"] == "success"
    assert evidence["token_usage"]["native"] == 100
    assert evidence["token_usage"]["status"] == "suspicious"

def test_run_tokenizer_probe_estimated():
    adapter = MockAdapter(native_usage=None)
    payload = {"input_type": "test", "content": "hello world"}

    evidence = run_tokenizer_probe(adapter, "mock-model", payload)

    assert evidence["status"] == "success"
    assert evidence["token_usage"]["native"] is None
    assert evidence["token_usage"]["status"] == "estimated"

def test_run_tokenizer_probe_error():
    adapter = ErrorMockAdapter()
    payload = {"input_type": "test", "content": "hello world"}

    evidence = run_tokenizer_probe(adapter, "mock-model", payload)

    assert evidence["status"] == "failed"
    assert "Provider error" in evidence["error"]

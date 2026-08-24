import json
from typing import Any, Dict, List

from ai_api_model_auditor.adapters.base import BaseAdapter
from ai_api_model_auditor.probes.streaming import probe_streaming


class MockAdapter(BaseAdapter):
    def get_provider_name(self) -> str:
        return "mock_provider"

    def list_models(self) -> List[str]:
        return ["mock-model-1"]

    def chat(
        self, model: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        assert kwargs.get("stream") is True, "Expected 'stream' to be True"
        return {
            "content": "streaming simulated chunk",
            "raw_response": {
                "choices": [{"delta": {"content": "streaming simulated chunk"}}]
            },
            "status_code": 200,
            "headers": {},
        }


def test_probe_streaming_success():
    adapter = MockAdapter()
    result = probe_streaming(adapter, "mock-model-1")

    assert result["provider"] == "mock_provider"
    assert result["probe"] == "streaming"
    assert result["model"] == "mock-model-1"
    assert result["status"] == "success"
    assert result["error"] is None
    assert "choices" in result["raw_response"]


def test_probe_streaming_json_error():
    class JSONErrorAdapter(MockAdapter):
        def chat(
            self, model: str, messages: List[Dict[str, str]], **kwargs
        ) -> Dict[str, Any]:
            raise json.JSONDecodeError("Expecting value", "", 0)

    adapter = JSONErrorAdapter()
    result = probe_streaming(adapter, "mock-model-1")

    assert result["status"] == "success"
    assert "sse_error_or_decode" in result["raw_response"]


def test_probe_streaming_exception():
    class FailingAdapter(MockAdapter):
        def chat(
            self, model: str, messages: List[Dict[str, str]], **kwargs
        ) -> Dict[str, Any]:
            raise ValueError("Streaming execution failed")

    adapter = FailingAdapter()
    result = probe_streaming(adapter, "mock-model-1")

    assert result["status"] == "failed"
    assert "Streaming execution failed" in result["error"]

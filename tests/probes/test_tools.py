from typing import Any, Dict, List

from ai_api_model_auditor.adapters.base import BaseAdapter
from ai_api_model_auditor.probes.tools import probe_tools


class MockAdapter(BaseAdapter):
    def get_provider_name(self) -> str:
        return "mock_provider"

    def list_models(self) -> List[str]:
        return ["mock-model-1"]

    def chat(
        self, model: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        assert "tools" in kwargs, "Expected 'tools' in kwargs"
        return {
            "content": "tool call simulation",
            "raw_response": {
                "tool_calls": [{"name": "get_weather", "arguments": "{}"}]
            },
            "status_code": 200,
            "headers": {},
        }


def test_probe_tools_success():
    adapter = MockAdapter()
    result = probe_tools(adapter, "mock-model-1")

    assert result["provider"] == "mock_provider"
    assert result["probe"] == "tools"
    assert result["model"] == "mock-model-1"
    assert result["status"] == "success"
    assert result["error"] is None
    assert "tool_calls" in result["raw_response"]


def test_probe_tools_exception():
    class FailingAdapter(MockAdapter):
        def chat(
            self, model: str, messages: List[Dict[str, str]], **kwargs
        ) -> Dict[str, Any]:
            raise ValueError("Tool execution failed")

    adapter = FailingAdapter()
    result = probe_tools(adapter, "mock-model-1")

    assert result["status"] == "failed"
    assert "Tool execution failed" in result["error"]

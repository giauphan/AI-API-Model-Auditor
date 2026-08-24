from typing import Any, Dict, List

import httpx

from ai_api_model_auditor.adapters.base import BaseAdapter
from ai_api_model_auditor.probes.errors import probe_errors


class MockAdapter(BaseAdapter):
    def get_provider_name(self) -> str:
        return "mock_provider"

    def list_models(self) -> List[str]:
        return ["mock-model-1"]

    def chat(
        self, model: str, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        has_invalid = any(msg.get("role") == "invalid_role_test" for msg in messages)
        if has_invalid:
            request = httpx.Request("POST", "http://mock")
            response = httpx.Response(
                400, request=request, text='{"error": {"message": "Invalid role"}}'
            )
            raise httpx.HTTPStatusError(
                "400 Bad Request", request=request, response=response
            )
        return {
            "content": "success",
            "raw_response": {},
            "status_code": 200,
            "headers": {},
        }


def test_probe_errors_captures_error():
    adapter = MockAdapter()
    result = probe_errors(adapter, "mock-model-1")

    assert result["provider"] == "mock_provider"
    assert result["probe"] == "errors"
    assert result["model"] == "mock-model-1"
    assert result["status"] == "success"
    assert result["error_captured"] is True
    assert "400 Bad Request" in result["error_details"]
    assert '{"error": {"message": "Invalid role"}}' in result["error_body"]


def test_probe_errors_misses_error():
    class MissingErrorAdapter(MockAdapter):
        def chat(
            self, model: str, messages: List[Dict[str, str]], **kwargs
        ) -> Dict[str, Any]:
            return {
                "content": "unexpected success",
                "raw_response": {},
                "status_code": 200,
                "headers": {},
            }

    adapter = MissingErrorAdapter()
    result = probe_errors(adapter, "mock-model-1")

    assert result["status"] == "failed"
    assert result["error_captured"] is False
    assert result["error_details"] == "Did not receive an error for malformed input"

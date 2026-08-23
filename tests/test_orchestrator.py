import pytest
from unittest.mock import patch, MagicMock

from ai_api_model_auditor.orchestrator import Orchestrator
from ai_api_model_auditor.config import AppConfig
from ai_api_model_auditor.adapters.base import BaseAdapter

class MockAdapter(BaseAdapter):
    def get_provider_name(self):
        return "mock"

    def list_models(self):
        return ["mock-model"]

    def chat(self, model, messages, **kwargs):
        return {
            "content": "mock content",
            "raw_response": {"mock": "data"},
            "status_code": 200,
            "headers": {}
        }

def test_orchestrator_quick_scan_dry_run():
    orchestrator = Orchestrator()
    config = AppConfig()

    result = orchestrator.run_quick_scan("openai", "dummy-model", config, dry_run=True)

    assert result["status"] == "success"
    assert "evidence_path" in result
    assert "Dry run" in result["message"]

@patch('ai_api_model_auditor.orchestrator.get_adapter')
def test_orchestrator_quick_scan_live_mocked(mock_get_adapter, tmp_path):
    # Setup mock adapter
    mock_adapter = MockAdapter()
    mock_get_adapter.return_value = mock_adapter

    orchestrator = Orchestrator()
    # Change store dir so we don't pollute actual evidence dir during tests
    orchestrator.store.output_dir = tmp_path

    config = AppConfig(openai_api_key="test")

    result = orchestrator.run_quick_scan("openai", "dummy-model", config, dry_run=False)

    assert result["status"] == "success"
    assert "evidence_path" in result
    assert result["evidence_path"].startswith(str(tmp_path))
    assert len(result["observations"]) == 2  # 2 basic probes

    for obs in result["observations"]:
        assert obs["status"] == "success"
        assert obs["response"] == "mock content"

@patch('ai_api_model_auditor.orchestrator.get_adapter')
def test_orchestrator_quick_scan_error(mock_get_adapter, tmp_path):
    # Setup mock adapter to throw error
    mock_get_adapter.side_effect = ValueError("Mock failure")

    orchestrator = Orchestrator()
    orchestrator.store.output_dir = tmp_path

    config = AppConfig()

    result = orchestrator.run_quick_scan("openai", "dummy-model", config, dry_run=False)

    assert result["status"] == "error"
    assert "Mock failure" in result["message"]
    assert "evidence_path" in result

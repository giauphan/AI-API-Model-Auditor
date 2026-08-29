import pytest
import json
from unittest.mock import MagicMock
from src.modelaudit.probes.reasoning import run_reasoning_probes, check_constraint, check_verbosity, sanitize_data

def test_check_constraint():
    assert check_constraint("One two three", "word_count_3") is True
    assert check_constraint("One two three four", "word_count_3") is False

def test_check_verbosity():
    assert check_verbosity("short") == "concise"
    assert check_verbosity("word " * 25) == "moderate"
    assert check_verbosity("word " * 105) == "verbose"

def test_sanitize_data():
    data = {"secret_key": "sk-12345678901234567890123456789012"}
    sanitized = sanitize_data(data)
    assert "sk-" not in sanitized["secret_key"]
    assert sanitized["secret_key"] == "***REDACTED***"

def test_run_reasoning_probes_success(tmp_path):
    mock_adapter = MagicMock()
    mock_adapter.get_provider_name.return_value = "mock_provider"

    def mock_chat(model, messages, **kwargs):
        content = ""
        prompt = messages[-1]["content"]
        if "implies" in prompt:
            content = "Yes"
        return {"content": content}

    mock_adapter.chat.side_effect = mock_chat

    cases = [{"name": "deterministic_logic", "prompt": "implies", "expected_content_contains": "Yes"}]
    cases_file = tmp_path / "cases.json"
    cases_file.write_text(json.dumps(cases))

    findings = run_reasoning_probes(mock_adapter, ["test_model"], str(cases_file))

    assert len(findings) == 1
    assert findings[0]["status"] == "pass"
    assert findings[0]["evidence"]["self_correction_triggered"] is False

def test_run_reasoning_probes_self_correction_success(tmp_path):
    mock_adapter = MagicMock()
    mock_adapter.get_provider_name.return_value = "mock_provider"

    def mock_chat(model, messages, **kwargs):
        if len(messages) == 1:
            return {"content": "Wrong answer initially"}
        elif len(messages) == 3 and "Are you sure?" in messages[-1]["content"]:
             return {"content": "Yes, I am sure. The answer is 180"}
        return {"content": "unknown"}

    mock_adapter.chat.side_effect = mock_chat

    cases = [{"name": "math", "prompt": "15 * 12", "expected_content_contains": "180"}]
    cases_file = tmp_path / "cases.json"
    cases_file.write_text(json.dumps(cases))

    findings = run_reasoning_probes(mock_adapter, ["test_model"], str(cases_file))

    assert len(findings) == 1
    assert findings[0]["status"] == "pass_after_correction"
    assert findings[0]["evidence"]["self_correction_triggered"] is True

def test_run_reasoning_probes_failure(tmp_path):
    mock_adapter = MagicMock()
    mock_adapter.get_provider_name.return_value = "mock_provider"
    mock_adapter.chat.return_value = {"content": "Always wrong"}

    cases = [{"name": "math", "prompt": "15 * 12", "expected_content_contains": "180"}]
    cases_file = tmp_path / "cases.json"
    cases_file.write_text(json.dumps(cases))

    findings = run_reasoning_probes(mock_adapter, ["test_model"], str(cases_file))

    assert len(findings) == 1
    assert findings[0]["status"] == "fail"
    assert findings[0]["evidence"]["self_correction_triggered"] is True

def test_run_reasoning_probes_error(tmp_path):
    mock_adapter = MagicMock()
    mock_adapter.get_provider_name.return_value = "mock_provider"
    mock_adapter.chat.side_effect = Exception("API error")

    cases = [{"name": "math", "prompt": "15 * 12", "expected_content_contains": "180"}]
    cases_file = tmp_path / "cases.json"
    cases_file.write_text(json.dumps(cases))

    findings = run_reasoning_probes(mock_adapter, ["test_model"], str(cases_file))

    assert len(findings) == 1
    assert findings[0]["status"] == "error"
    assert "API error" in findings[0]["evidence"]["error"]

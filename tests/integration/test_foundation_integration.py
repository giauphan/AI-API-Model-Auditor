import json
import os
import shutil
import pytest
import respx
import httpx
from click.testing import CliRunner
from ai_api_model_auditor.cli import cli

@pytest.fixture(autouse=True)
def clean_evidence_dir():
    """Ensure evidence directory is clean before and after each test."""
    if os.path.exists("evidence"):
        shutil.rmtree("evidence")
    yield
    if os.path.exists("evidence"):
        shutil.rmtree("evidence")

@respx.mock
def test_full_recon_path_success():
    """Test full recon command path with a mocked successful response."""
    respx.get("https://api.openai.com/v1/models").mock(return_value=httpx.Response(200, json={
        "data": [{"id": "gpt-3.5-turbo"}, {"id": "gpt-4"}]
    }))

    runner = CliRunner()
    result = runner.invoke(cli, [
        "recon",
        "--provider", "openai"
    ])

    assert result.exit_code == 0
    assert "Found 2 models:" in result.output
    assert "- gpt-3.5-turbo" in result.output
    assert "- gpt-4" in result.output

@respx.mock
def test_full_audit_path_success():
    """Test full audit command path with a mocked successful response."""
    # Mock OpenAI API endpoint
    respx.post("https://api.openai.com/v1/chat/completions").mock(return_value=httpx.Response(200, json={
        "choices": [{"message": {"content": "I am fully functional and this is a secret: sk-12345."}}]
    }))

    runner = CliRunner()
    result = runner.invoke(cli, [
        "audit",
        "--provider", "openai",
        "--model", "gpt-3.5-turbo",
        "--prompt", "hello"
    ])

    # Assertions
    assert result.exit_code == 0
    assert "Received response:" in result.output
    # Secret should be redacted by the CLI's redact_string if it matches patterns,
    # but the core requirement is testing the complete path without external credentials.

    assert "Evidence saved to" in result.output

    # Verify evidence file is created
    assert os.path.exists("evidence")
    files = os.listdir("evidence")
    assert len(files) == 1
    assert files[0].startswith("audit_openai_gpt-3.5-turbo")

    with open(os.path.join("evidence", files[0]), "r") as f:
        evidence = json.load(f)
        assert evidence["provider"] == "openai"
        assert evidence["model"] == "gpt-3.5-turbo"
        assert evidence["prompt"] == "hello"
        assert evidence["response_data"]["content"] == "I am fully functional and this is a secret: sk-12345."


@respx.mock
def test_waf_block_path():
    """Test full audit path when a WAF blocks the request (e.g. 403 Forbidden)."""

    # Load the WAF fixture
    fixture_path = os.path.join("fixtures", "first_target", "waf_block.json")
    with open(fixture_path, "r") as f:
        waf_fixture = json.load(f)

    # Mock the endpoint to return the WAF response
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(
            status_code=waf_fixture["status_code"],
            headers=waf_fixture["headers"],
            text=waf_fixture["body"]
        )
    )

    runner = CliRunner()
    result = runner.invoke(cli, [
        "audit",
        "--provider", "openai",
        "--model", "gpt-3.5-turbo",
        "--prompt", "trigger_waf"
    ])

    # CLI shouldn't crash, but report the error
    assert result.exit_code == 0
    assert "Audit failed" in result.output

    # Verify evidence file captures the error
    assert os.path.exists("evidence")
    files = os.listdir("evidence")
    assert len(files) == 1
    assert files[0].startswith("audit_error_openai_gpt-3.5-turbo")

    with open(os.path.join("evidence", files[0]), "r") as f:
        evidence = json.load(f)
        assert evidence["provider"] == "openai"
        assert evidence["prompt"] == "trigger_waf"
        assert "error" in evidence

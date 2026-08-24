import pytest
import respx
import httpx
from ai_api_model_auditor.adapters import get_adapter
from ai_api_model_auditor.config import AppConfig

@pytest.fixture
def config():
    return AppConfig(
        openai_api_key="test-openai-key",
        anthropic_api_key="test-anthropic-key",
        gemini_api_key="test-gemini-key"
    )

@respx.mock
def test_openai_adapter_list_models(config):
    respx.get("https://api.openai.com/v1/models").mock(return_value=httpx.Response(200, json={
        "data": [{"id": "gpt-3.5-turbo"}, {"id": "gpt-4"}]
    }))
    adapter = get_adapter("openai", config)
    models = adapter.list_models()
    assert models == ["gpt-3.5-turbo", "gpt-4"]

@respx.mock
def test_openai_adapter_chat(config):
    respx.post("https://api.openai.com/v1/chat/completions").mock(return_value=httpx.Response(200, json={
        "choices": [{"message": {"content": "Hello there!"}}]
    }))
    adapter = get_adapter("openai", config)
    res = adapter.chat("gpt-4", [{"role": "user", "content": "hi"}])
    assert res["content"] == "Hello there!"
    assert res["status_code"] == 200

@respx.mock
def test_anthropic_adapter_chat(config):
    respx.post("https://api.anthropic.com/v1/messages").mock(return_value=httpx.Response(200, json={
        "content": [{"text": "Greetings human."}]
    }))
    adapter = get_adapter("anthropic", config)
    res = adapter.chat("claude-3-opus", [{"role": "user", "content": "hi"}])
    assert res["content"] == "Greetings human."
    assert res["status_code"] == 200

@respx.mock
def test_gemini_adapter_chat(config):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=test-gemini-key"
    respx.post(url).mock(return_value=httpx.Response(200, json={
        "candidates": [{"content": {"parts": [{"text": "Hi from Gemini"}]}}]
    }))
    adapter = get_adapter("gemini", config)
    res = adapter.chat("gemini-pro", [{"role": "user", "content": "hi"}])
    assert res["content"] == "Hi from Gemini"
    assert res["status_code"] == 200

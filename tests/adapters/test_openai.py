
import httpx
import pytest
import respx

from ai_api_model_auditor.adapters.openai import OpenAIAdapter
from ai_api_model_auditor.config import AppConfig
from ai_api_model_auditor.http_client import AuthError, MalformedResponseError


@pytest.fixture
def config():
    return AppConfig(openai_api_key="test-key", base_url="https://api.openai.com/v1")


@pytest.fixture
def adapter(config):
    return OpenAIAdapter(config)


@respx.mock
def test_openai_list_models_success(adapter):
    respx.get("https://api.openai.com/v1/models").mock(
        return_value=httpx.Response(
            200, json={"data": [{"id": "gpt-4"}, {"id": "gpt-3.5"}]}
        )
    )
    models = adapter.list_models()
    assert models == ["gpt-4", "gpt-3.5"]


@respx.mock
def test_openai_list_models_auth_error(adapter):
    respx.get("https://api.openai.com/v1/models").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    with pytest.raises(AuthError):
        adapter.list_models()


@respx.mock
def test_openai_list_models_malformed_json(adapter):
    respx.get("https://api.openai.com/v1/models").mock(
        return_value=httpx.Response(200, text="Not a JSON")
    )
    with pytest.raises(MalformedResponseError, match="Failed to parse JSON response"):
        adapter.list_models()


@respx.mock
def test_openai_list_models_unexpected_structure(adapter):
    respx.get("https://api.openai.com/v1/models").mock(
        return_value=httpx.Response(200, json={"unexpected": "structure"})
    )
    with pytest.raises(MalformedResponseError, match="Unexpected response structure"):
        adapter.list_models()


@respx.mock
def test_openai_chat_success(adapter):
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(
            200, json={"choices": [{"message": {"content": "Hello!"}}]}
        )
    )
    res = adapter.chat("gpt-4", [{"role": "user", "content": "Hi"}])
    assert res["content"] == "Hello!"
    assert res["status_code"] == 200


@respx.mock
def test_openai_chat_auth_error(adapter):
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(403, text="Forbidden")
    )
    with pytest.raises(AuthError):
        adapter.chat("gpt-4", [{"role": "user", "content": "Hi"}])


@respx.mock
def test_openai_chat_malformed_json(adapter):
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(200, text="Not a JSON")
    )
    with pytest.raises(MalformedResponseError):
        adapter.chat("gpt-4", [{"role": "user", "content": "Hi"}])


@respx.mock
def test_openai_chat_streaming(adapter):
    # Test valid streaming
    def content_iterator():
        yield b'data: {"choices": [{"delta": {"content": "He"}}]}\n'
        yield b'data: {"choices": [{"delta": {"content": "llo!"}}]}\n'
        yield b"data: [DONE]\n"

    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(200, content=content_iterator())
    )

    res = adapter.chat("gpt-4", [{"role": "user", "content": "Hi"}], stream=True)
    assert "stream" in res
    stream_gen = res["stream"]
    chunks = list(stream_gen)
    assert len(chunks) == 2
    assert chunks[0]["choices"][0]["delta"]["content"] == "He"
    assert chunks[1]["choices"][0]["delta"]["content"] == "llo!"


@respx.mock
def test_openai_chat_streaming_malformed_lines_and_fragmented(adapter):
    # Test streaming handles bad JSON and terminal events properly without breaking the whole stream
    def content_iterator():
        yield b'data: {"choices": [{"delta": {"content": "1"}}]}\n'
        yield b"data: not valid json\n"
        yield b'data: {"choices": [{"delta": {"content": "2"}}]}\n'
        yield b"data: [DONE]\n"
        yield b'data: {"choices": [{"delta": {"content": "ignored"}}]}\n'

    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(200, content=content_iterator())
    )

    res = adapter.chat("gpt-4", [{"role": "user", "content": "Hi"}], stream=True)
    stream_gen = res["stream"]
    chunks = list(stream_gen)

    assert len(chunks) == 2
    assert chunks[0]["choices"][0]["delta"]["content"] == "1"
    assert chunks[1]["choices"][0]["delta"]["content"] == "2"

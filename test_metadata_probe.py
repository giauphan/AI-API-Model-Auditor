from probe_modules.metadata import MetadataProbe
import hashlib


def test_metadata_probe_activate():
    probe = MetadataProbe()
    assert probe.activate() is True


def test_extract_metadata_openai_format():
    probe = MetadataProbe()
    response = {
        "model": "gpt-3.5-turbo-0613",
        "id": "chatcmpl-123",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
        "choices": [{"finish_reason": "stop"}],
        "headers": {
            "x-ratelimit-limit": "100",
            "authorization": "Bearer sk-123",
        },
        "latency": 0.5,
    }
    requested_model = "gpt-3.5-turbo"
    raw_response = '{"model": "gpt-3.5-turbo-0613"}'
    raw_req = {
        "messages": [{"role": "user", "content": "sk-abc"}],
        "headers": {"Authorization": "sk-def"},
    }

    observations = probe.extract_metadata(
        response,
        requested_model,
        raw_request=raw_req,
        raw_response=raw_response,
    )

    assert len(observations) == 2  # 1 for mismatch, 1 for metadata

    mismatch_obs = [o for o in observations if o.type == "model_mismatch"][0]
    assert mismatch_obs.data["requested"] == "gpt-3.5-turbo"
    assert mismatch_obs.data["returned"] == "gpt-3.5-turbo-0613"
    assert mismatch_obs.evidence_strength == "high"

    meta_obs = [o for o in observations if o.type == "response_metadata"][0]
    metadata = meta_obs.data
    assert metadata["requested_model"] == "gpt-3.5-turbo"
    assert metadata["returned_model"] == "gpt-3.5-turbo-0613"
    assert metadata["response_id"] == "chatcmpl-123"
    assert metadata["finish_reason"] == "stop"
    assert metadata["usage"]["total_tokens"] == 30
    assert metadata["headers"]["x-ratelimit-limit"] == "100"

    # Check redaction in headers
    assert metadata["headers"]["authorization"] == "Bearer [REDACTED]"

    assert metadata["latency"] == 0.5
    raw_hash = hashlib.sha256(raw_response.encode("utf-8")).hexdigest()
    assert metadata["raw_response_hash"] == raw_hash

    # Check raw request capture and redaction
    assert metadata["raw_request_captured"] is True
    assert metadata["raw_request"]["messages"][0]["content"] == "[REDACTED]"
    assert metadata["raw_request"]["headers"]["Authorization"] == "[REDACTED]"


def test_extract_metadata_anthropic_format():
    probe = MetadataProbe()
    response = {
        "model": "claude-3-haiku-20240307",
        "id": "msg_123",
        "usage": {"input_tokens": 15, "output_tokens": 25},
        "stop_reason": "end_turn",
        "content": [{"text": "Hello"}],
    }
    requested_model = "claude-3-haiku-20240307"

    observations = probe.extract_metadata(response, requested_model)

    assert len(observations) == 1

    meta_obs = [o for o in observations if o.type == "response_metadata"][0]
    metadata = meta_obs.data
    assert metadata["requested_model"] == "claude-3-haiku-20240307"
    assert metadata["returned_model"] == "claude-3-haiku-20240307"
    assert metadata["response_id"] == "msg_123"
    assert metadata["finish_reason"] == "end_turn"


def test_extract_metadata_invalid_response():
    probe = MetadataProbe()
    observations = probe.extract_metadata("invalid string response", "model")
    assert len(observations) == 1
    assert observations[0].type == "error"

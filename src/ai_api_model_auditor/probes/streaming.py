import json
from typing import Any, Dict

from ..adapters.base import BaseAdapter


def probe_streaming(adapter: BaseAdapter, model: str) -> Dict[str, Any]:
    """
    Perform a streaming behavior probe on an endpoint.
    Tests SSE chunk/event behavior.
    Returns a dictionary of structured observations.
    """
    findings = {
        "provider": adapter.get_provider_name(),
        "probe": "streaming",
        "model": model,
        "status": "success",
        "error": None,
        "raw_response": None,
    }

    messages = [
        {"role": "user", "content": "Tell me a very short story about a brave knight."}
    ]

    try:
        # Check if the adapter supports stream directly via chat.
        # If it returns JSON, it might throw a decode error if the response is actually an SSE stream.
        # For now, we capture the exception as the fingerprint or capability test.
        try:
            response = adapter.chat(model, messages, stream=True)
            findings["raw_response"] = response.get("raw_response", {})
        except json.JSONDecodeError as json_e:
            findings["raw_response"] = {"sse_error_or_decode": str(json_e)}
    except Exception as e:
        findings["status"] = "failed"
        findings["error"] = str(e)

    return findings

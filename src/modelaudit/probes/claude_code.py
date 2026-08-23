from typing import Any, Dict


def probe_claude_code(adapter, model: str) -> Dict[str, Any]:
    """
    Probes specific Anthropic behavior for Claude Code compatibility, including
    cache-control, streaming, thinking, tools, system blocks, and regular messages.
    """
    findings = {
        "provider": adapter.get_provider_name(),
        "model": model,
        "features": {
            "system_blocks": "untested",
            "tools": "untested",
            "streaming": "untested",
            "thinking": "untested",
            "cache_control": "untested",
            "messages": "untested",
        },
        "status": "success",
        "error": None,
    }

    test_payload = {
        "system": "You are a helpful assistant.",
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current weather",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                    },
                },
            }
        ],
        "stream": True,
        "thinking": {"type": "enabled", "budget_tokens": 1024},
        "cache_control": {"type": "ephemeral"},
    }

    messages = [
        {
            "role": "user",
            "content": "Hello, how are you? What is the weather in London?",
        }
    ]

    try:
        # Try full feature set
        adapter.chat(model, messages, **test_payload)

        # If it doesn't fail, we assume it accepted the payload
        findings["features"]["system_blocks"] = "supported"
        findings["features"]["tools"] = "supported"
        findings["features"]["streaming"] = "supported"
        findings["features"]["thinking"] = "supported"
        findings["features"]["cache_control"] = "supported"
        findings["features"]["messages"] = "supported"

    except Exception as e:
        findings["status"] = "failed"
        findings["error"] = str(e)

    return findings

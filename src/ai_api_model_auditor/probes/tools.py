from typing import Any, Dict

from ..adapters.base import BaseAdapter


def probe_tools(adapter: BaseAdapter, model: str) -> Dict[str, Any]:
    """
    Perform a tool behavior probe on an endpoint.
    Tests Tool-choice/schema/escaping/parallel-call behavior.
    Returns a dictionary of structured observations.
    """
    findings = {
        "provider": adapter.get_provider_name(),
        "probe": "tools",
        "model": model,
        "status": "success",
        "error": None,
        "raw_response": None,
    }

    messages = [
        {
            "role": "user",
            "content": "What is the weather like in New York and San Francisco?",
        }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]

    try:
        # Prompt model to make potentially parallel tool calls
        response = adapter.chat(model, messages, tools=tools)
        findings["raw_response"] = response.get("raw_response", {})
    except Exception as e:
        findings["status"] = "failed"
        findings["error"] = str(e)

    return findings

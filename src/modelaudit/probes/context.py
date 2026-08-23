from typing import Dict, Any, List

def generate_context_payloads() -> List[Dict[str, Any]]:
    """
    Generates payloads for bounded context-window probing and structured needle tests.
    """
    return [
        {
            "test_name": "retrieval_success",
            "haystack_size": 500,
            "needle": "SECRET_CODE_123",
            "instruction": "What is the secret code hidden in the text?",
            "expected": "SECRET_CODE_123",
            "position": "middle"
        },
        {
            "test_name": "context_failure",
            "haystack_size": 2000,
            "needle": "HIDDEN_TREASURE_456",
            "instruction": "Find the hidden treasure code.",
            "expected": "HIDDEN_TREASURE_456",
            "position": "start"
        }
    ]

def _build_haystack(size: int, needle: str, position: str) -> str:
    """
    Builds a bounded haystack of filler text with a needle inserted.
    """
    filler = "This is some filler text to create a context window. "

    num_filler = size // len(filler.split())
    if num_filler <= 0:
        num_filler = 10

    parts = [filler] * num_filler

    if position == "start":
        parts.insert(0, f" Here is the hidden information: {needle}. ")
    elif position == "middle":
        mid = len(parts) // 2
        parts.insert(mid, f" Here is the hidden information: {needle}. ")
    elif position == "end":
        parts.append(f" Here is the hidden information: {needle}. ")

    return "".join(parts)

def run_context_probe(adapter: Any, model: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs a bounded context window / needle-in-a-haystack probe.
    """
    haystack = _build_haystack(payload["haystack_size"], payload["needle"], payload["position"])

    prompt = f"{haystack}\n\nQuestion: {payload['instruction']}"

    messages = [{"role": "user", "content": prompt}]

    evidence = {
        "probe_type": "context_window",
        "test_name": payload["test_name"],
        "provider": getattr(adapter, 'get_provider_name', lambda: "unknown")(),
        "model": model,
        "haystack_size_chars": len(haystack),
        "needle": payload["needle"],
        "position": payload["position"],
        "status": "failed",
        "retrieval_status": "unknown"
    }

    try:
        response = adapter.chat(model, messages, max_tokens=50)

        evidence["status"] = "success"

        content = response.get("content", "")

        if payload["expected"] in content:
            evidence["retrieval_status"] = "success"
        else:
            evidence["retrieval_status"] = "failed"

        evidence["response_excerpt"] = content[:100]

    except Exception as e:
        evidence["error"] = str(e)
        evidence["retrieval_status"] = "error"

    return evidence

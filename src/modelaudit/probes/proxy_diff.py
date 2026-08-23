from typing import Any, Dict


def probe_proxy_diff(adapter_a, adapter_b, model: str) -> Dict[str, Any]:
    """
    Compares responses between two adapters (e.g. direct API vs proxy API)
    for the same model and prompt to identify differences.
    """
    findings = {
        "model": model,
        "adapter_a_provider": adapter_a.get_provider_name(),
        "adapter_b_provider": adapter_b.get_provider_name(),
        "content_diff": False,
        "adapter_a_response": None,
        "adapter_b_response": None,
        "status": "success",
        "error": None,
    }

    messages = [{"role": "user", "content": "Hello."}]

    try:
        response_a = adapter_a.chat(model, messages)
        response_b = adapter_b.chat(model, messages)

        content_a = response_a.get("content", "")
        content_b = response_b.get("content", "")

        findings["adapter_a_response"] = content_a
        findings["adapter_b_response"] = content_b

        if content_a != content_b:
            findings["content_diff"] = True

    except Exception as e:
        findings["status"] = "failed"
        findings["error"] = str(e)

    return findings

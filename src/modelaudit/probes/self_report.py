from typing import Dict, Any


def probe_self_report(adapter, model: str) -> Dict[str, Any]:
    """
    Probes the model for its self-reported identity.
    """
    findings = {
        "provider": adapter.get_provider_name(),
        "model": model,
        "self_reported_identity": None,
        "weight": "very low",
        "status": "success",
        "error": None,
    }

    prompt = "What is your underlying model name and version?"
    messages = [{"role": "user", "content": prompt}]

    try:
        response = adapter.chat(model, messages)
        content = response.get("content", "")
        findings["self_reported_identity"] = content

    except Exception as e:
        findings["status"] = "failed"
        findings["error"] = str(e)

    return findings

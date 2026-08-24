from typing import Dict, Any


def probe_thinking(adapter, model: str) -> Dict[str, Any]:
    """
    Probes if the model exposes its reasoning or thinking separately from its final answer.
    """
    findings = {
        "provider": adapter.get_provider_name(),
        "model": model,
        "reasoning": None,
        "identity_evidence": None,
        "status": "success",
        "error": None,
    }

    prompt = "Explain step-by-step why 2+2=4. Output your reasoning first, then 'FINAL_ANSWER: 4'."
    messages = [{"role": "user", "content": prompt}]

    try:
        response = adapter.chat(model, messages)
        content = response.get("content", "")

        if "FINAL_ANSWER:" in content:
            parts = content.split("FINAL_ANSWER:", 1)
            findings["reasoning"] = parts[0].strip()
            findings["identity_evidence"] = parts[1].strip()
        else:
            findings["identity_evidence"] = content

    except Exception as e:
        findings["status"] = "failed"
        findings["error"] = str(e)

    return findings

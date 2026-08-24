from typing import Dict, Any


def probe_seed_stability(adapter, model: str, seed: int = 42) -> Dict[str, Any]:
    """
    Probes if the model output is stable when the same seed and temperature 0 are provided.
    """
    findings = {
        "provider": adapter.get_provider_name(),
        "model": model,
        "seed_tested": seed,
        "seed_stability": "unknown",
        "status": "success",
        "error": None,
    }

    messages = [{"role": "user", "content": "Write a short poem about auditing."}]

    try:
        response1 = adapter.chat(model, messages, seed=seed, temperature=0.0)
        response2 = adapter.chat(model, messages, seed=seed, temperature=0.0)

        content1 = response1.get("content", "")
        content2 = response2.get("content", "")

        if content1 and content2 and content1 == content2:
            findings["seed_stability"] = "stable"
        else:
            findings["seed_stability"] = "unstable"

    except Exception as e:
        findings["status"] = "failed"
        findings["error"] = str(e)
        findings["seed_stability"] = "unsupported"

    return findings

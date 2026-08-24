from typing import Any, Dict

import httpx

from ..adapters.base import BaseAdapter


def probe_errors(adapter: BaseAdapter, model: str) -> Dict[str, Any]:
    """
    Perform an error footprint probe on an endpoint.
    Tests API behavior when provided malformed input, capturing error fingerprints.
    Returns a dictionary of structured observations.
    """
    findings = {
        "provider": adapter.get_provider_name(),
        "probe": "errors",
        "model": model,
        "status": "success",
        "error_captured": False,
        "error_details": None,
        "error_body": None,
    }

    # Deliberately malformed messages
    messages = [{"role": "invalid_role_test", "content": "This should fail."}]

    try:
        adapter.chat(model, messages)
        findings["status"] = "failed"  # Expected an error but didn't get one
        findings["error_details"] = "Did not receive an error for malformed input"
    except httpx.HTTPStatusError as e:
        findings["error_captured"] = True
        findings["error_details"] = str(e)
        try:
            findings["error_body"] = e.response.text
        except Exception:
            pass
    except Exception as e:
        findings["error_captured"] = True
        findings["error_details"] = str(e)

    return findings

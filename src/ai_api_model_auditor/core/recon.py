from typing import List, Dict, Any
from ..adapters.base import BaseAdapter

def enumerate_models(adapter: BaseAdapter) -> List[str]:
    """
    Given an adapter, lists all models available.
    """
    try:
        models = adapter.list_models()
        return models
    except Exception as e:
        # In a real auditor, we might log the exception.
        # Here we just raise it or return an empty list depending on error tolerance.
        raise e

def probe_endpoint(adapter: BaseAdapter, models: List[str] = None) -> Dict[str, Any]:
    """
    Perform a basic reconnaissance probe on an endpoint.
    If models aren't provided, attempts to enumerate them.
    Returns a dictionary of findings.
    """
    findings = {
        "provider": adapter.get_provider_name(),
        "models_discovered": [],
        "status": "success",
        "error": None
    }

    try:
        if not models:
            models = enumerate_models(adapter)

        findings["models_discovered"] = models

    except Exception as e:
        findings["status"] = "failed"
        findings["error"] = str(e)

    return findings

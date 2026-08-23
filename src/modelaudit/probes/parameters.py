from typing import Dict, Any


def probe_parameters(
    adapter, model: str, test_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Probes which parameters are accepted or rejected by the model endpoint.
    """
    capability_matrix = {}

    for param_name, param_value in test_params.items():
        try:
            adapter.chat(
                model,
                [{"role": "user", "content": "test"}],
                **{param_name: param_value},
            )
            capability_matrix[param_name] = "accepted"
        except Exception:
            capability_matrix[param_name] = "rejected"

    return {
        "provider": adapter.get_provider_name(),
        "model": model,
        "capability_matrix": capability_matrix,
        "status": "success",
        "error": None,
    }

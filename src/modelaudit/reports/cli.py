from typing import Any, Dict, List, Union

from .json import ReportData


def _format_list_or_str(val: Union[List[str], str, None], default: str = "None") -> str:
    if val is None:
        return default
    if isinstance(val, str):
        return val
    if not val:
        return default
    return ", ".join(val)


def _format_dict_or_list(
    val: Union[List[str], Dict[str, Any], None], default: str = "None"
) -> str:
    if val is None:
        return default
    if isinstance(val, list):
        if not val:
            return default
        return ", ".join(val)
    if isinstance(val, dict):
        if not val:
            return default
        return ", ".join(f"{k}: {v}" for k, v in val.items())
    return str(val)


def generate_cli_report(data: ReportData) -> str:
    """
    Generates a human-readable CLI report from the provided data.
    """
    lines = []
    lines.append("=== Model Audit Report ===")
    lines.append(f"Target: {data.get('target', 'Unknown')}")
    lines.append(f"Connectivity: {data.get('connectivity', False)}")
    status = data.get("advertised_callable_status", "Unknown")
    lines.append(f"Advertised/Callable Status: {status}")
    lines.append(f"Protocol: {data.get('protocol', 'Unknown')}")
    lines.append(f"Family Confidence: {data.get('family_confidence', 'Unknown')}")

    suspicion = _format_dict_or_list(data.get("suspicion_dimensions"))
    lines.append(f"Suspicion Dimensions: {suspicion}")

    lines.append(f"Strongest Evidence: {data.get('strongest_evidence', 'None')}")

    limitations = _format_list_or_str(data.get("limitations"))
    lines.append(f"Limitations: {limitations}")

    artifacts = data.get("artifact_paths", [])
    if artifacts:
        lines.append("Artifact Paths:")
        for path in artifacts:
            lines.append(f"  - {path}")
    else:
        lines.append("Artifact Paths: None")

    return "\n".join(lines)

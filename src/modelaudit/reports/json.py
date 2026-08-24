import json
from typing import Any, Dict, List, TypedDict, Union


class ReportData(TypedDict, total=False):
    target: str
    connectivity: bool
    advertised_callable_status: Union[str, bool]
    protocol: str
    family_confidence: Union[float, str]
    suspicion_dimensions: Union[List[str], Dict[str, Any]]
    strongest_evidence: str
    limitations: Union[List[str], str]
    artifact_paths: List[str]


def generate_json_report(data: ReportData) -> str:
    """
    Generates a machine-readable, stable JSON report from the provided data.
    """
    return json.dumps(data, sort_keys=True, indent=2)

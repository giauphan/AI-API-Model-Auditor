from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Observation:
    type: str
    data: Dict[str, Any]
    redacted: bool = True
    evidence_strength: str = "medium"

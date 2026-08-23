import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from ..safety import redact_string

class EvidenceStore:
    def __init__(self, output_dir: str = "evidence"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_data(self, data: Any) -> Any:
        """Recursively redact secrets from data before storing."""
        if isinstance(data, str):
            return redact_string(data)
        elif isinstance(data, dict):
            return {k: self._sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_data(i) for i in data]
        else:
            return data

    def save_evidence(self, name: str, data: Dict[str, Any]) -> str:
        """
        Saves structured evidence to a JSON file.
        Redacts any known secrets before writing to disk.

        Args:
            name: Base name for the evidence file.
            data: Dictionary containing the evidence.

        Returns:
            The path to the saved evidence file.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_name = name.replace("/", "_").replace(" ", "_")
        filename = f"{safe_name}_{timestamp}.json"
        filepath = self.output_dir / filename

        sanitized_data = self._sanitize_data(data)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(sanitized_data, f, indent=2, ensure_ascii=False)

        return str(filepath)

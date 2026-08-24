import json
import os
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from ..safety import redact_string

class EvidenceStore:
    def __init__(self, output_dir: str = "evidence"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.output_dir / "manifest.json"

        # Initialize manifest if it doesn't exist
        if not self.manifest_path.exists():
            self._save_manifest({"artifacts": []})

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

    def _save_manifest(self, data: Dict[str, Any]):
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _load_manifest(self) -> Dict[str, Any]:
        if not self.manifest_path.exists():
            return {"artifacts": []}
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _update_manifest(self, filename: str, hash_val: str, metadata: Dict[str, Any] = None):
        manifest = self._load_manifest()
        entry = {
            "file": filename,
            "sha256": hash_val,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        if metadata:
            entry.update(metadata)
        manifest["artifacts"].append(entry)
        self._save_manifest(manifest)

    def save_config(self, config_data: Dict[str, Any]) -> str:
        """Saves a redacted copy of the configuration."""
        filepath = self.output_dir / "config.redacted.json"
        sanitized_data = self._sanitize_data(config_data)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(sanitized_data, f, indent=2, ensure_ascii=False)

        file_hash = self._compute_hash(filepath)
        self._update_manifest("config.redacted.json", file_hash, {"type": "config"})

        return str(filepath)

    def _compute_hash(self, filepath: Path) -> str:
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def save_evidence(self, name: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Saves structured evidence to a JSON file.
        Redacts any known secrets before writing to disk.

        Args:
            name: Base name for the evidence file.
            data: Dictionary containing the evidence.
            metadata: Optional metadata to include in the manifest.

        Returns:
            The path to the saved evidence file.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        safe_name = name.replace("/", "_").replace(" ", "_")
        filename = f"{safe_name}_{timestamp}.json"
        filepath = self.output_dir / filename

        sanitized_data = self._sanitize_data(data)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(sanitized_data, f, indent=2, ensure_ascii=False)

        file_hash = self._compute_hash(filepath)
        self._update_manifest(filename, file_hash, metadata)

        return str(filepath)

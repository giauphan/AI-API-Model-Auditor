from typing import Dict, Any
from ai_api_model_auditor.adapters import get_adapter
from ai_api_model_auditor.storage.evidence import EvidenceStore
from ai_api_model_auditor.probes.basic import run_basic_probes

class Orchestrator:
    def __init__(self):
        self.store = EvidenceStore()

    def run_quick_scan(self, provider: str, model: str, config: Any, dry_run: bool = False) -> Dict[str, Any]:
        """
        Runs a quick scan against the specified provider and model using basic probes.
        """
        evidence_data = {
            "provider": provider,
            "model": model,
            "mode": "dry-run" if dry_run else "live",
            "scan_type": "quick",
            "findings": []
        }

        if dry_run:
            evidence_data["findings"] = [{"status": "simulated", "message": "Dry run mock evidence"}]
            path = self.store.save_evidence(f"quick_scan_{provider}_{model}", evidence_data)
            return {
                "status": "success",
                "message": "Dry run simulated successfully.",
                "evidence_path": path
            }

        try:
            adapter = get_adapter(provider, config)
            observations = run_basic_probes(adapter, model)

            evidence_data["findings"] = observations

            # Simple check if any probe succeeded
            any_success = any(obs.get("status") == "success" for obs in observations)
            status = "success" if any_success else "error"

            evidence_data["status"] = status

            path = self.store.save_evidence(f"quick_scan_{provider}_{model}", evidence_data)

            return {
                "status": status,
                "message": f"Completed basic probes. {len([o for o in observations if o.get('status') == 'success'])}/{len(observations)} succeeded.",
                "evidence_path": path,
                "observations": observations
            }

        except Exception as e:
            evidence_data["error"] = str(e)
            evidence_data["status"] = "error"
            path = self.store.save_evidence(f"quick_scan_error_{provider}_{model}", evidence_data)

            return {
                "status": "error",
                "message": str(e),
                "evidence_path": path
            }

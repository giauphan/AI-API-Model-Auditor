from typing import Any, Dict


class Replayer:
    """Replays a sanitized historical run."""

    def __init__(self, history_manager=None):
        self.history_manager = history_manager

    def replay_run(self, run_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replays a historical run by simulating its outputs without live network calls.

        Args:
            run_data: The sanitized dictionary representing the historical run.

        Returns:
            The simulated/replayed outputs (which should match the historical evidence).
        """
        if "provider" not in run_data or "model" not in run_data:
            raise ValueError("Invalid run data: missing provider or model")

        return {
            "status": "replayed",
            "provider": run_data.get("provider"),
            "model": run_data.get("model"),
            "original_run_date": run_data.get("run_date"),
            "results": run_data.get("results", {}),
        }

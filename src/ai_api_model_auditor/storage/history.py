import json
import sqlite3
from typing import Any, Dict, List, Optional


class HistoryManager:
    """Manages storage and retrieval of historical audit runs."""

    def __init__(self, db_path: str = "history.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    run_date TEXT NOT NULL,
                    data TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_run(self, run_data: Dict[str, Any]) -> int:
        """Saves a single audit run.

        Args:
            run_data: A dictionary containing the run data. Must contain
                      'provider', 'model', and 'run_date'.

        Returns:
            The ID of the inserted record.
        """
        provider = run_data.get("provider")
        model = run_data.get("model")
        run_date = run_data.get("run_date")

        if not provider or not model or not run_date:
            raise ValueError(
                "run_data must contain 'provider', 'model', and 'run_date'"
            )

        data_str = json.dumps(run_data)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO audit_runs (provider, model, run_date, data)
                VALUES (?, ?, ?, ?)
            """,
                (provider, model, run_date, data_str),
            )
            conn.commit()
            return cursor.lastrowid or 0

    def get_history(
        self, provider: str, model: str, date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves history for a given provider and model."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT data FROM audit_runs WHERE provider = ? AND model = ?"
            params = [provider, model]

            if date:
                query += " AND run_date = ?"
                params.append(date)

            cursor.execute(query, params)
            results = cursor.fetchall()

            return [json.loads(row[0]) for row in results]

    def detect_drift(self, run1: Dict[str, Any], run2: Dict[str, Any]) -> List[str]:
        """Detects historical drift between two runs.

        Checks for changes in:
        - family confidence
        - clusters
        - mapping
        - protocol

        Returns:
            A list of strings describing the detected drifts.
        """
        drifts = []

        # Helper to safely extract nested values
        def get_nested(d: dict, *keys: str) -> Any:
            current: Any = d
            for k in keys:
                if not isinstance(current, dict):
                    return None
                current = current.get(k)
            return current

        # Check family confidence drift
        conf1 = get_nested(run1, "results", "family_confidence")
        conf2 = get_nested(run2, "results", "family_confidence")
        if conf1 is not None and conf2 is not None and conf1 != conf2:
            drifts.append(f"Family confidence changed from {conf1} to {conf2}")

        # Check clusters drift
        clus1 = get_nested(run1, "results", "clusters")
        clus2 = get_nested(run2, "results", "clusters")
        if clus1 is not None and clus2 is not None and clus1 != clus2:
            drifts.append(f"Clusters changed from {clus1} to {clus2}")

        # Check mapping drift
        map1 = get_nested(run1, "results", "mapping")
        map2 = get_nested(run2, "results", "mapping")
        if map1 is not None and map2 is not None and map1 != map2:
            drifts.append(f"Mapping changed from {map1} to {map2}")

        # Check protocol drift
        prot1 = get_nested(run1, "results", "protocol")
        prot2 = get_nested(run2, "results", "protocol")
        if prot1 is not None and prot2 is not None and prot1 != prot2:
            drifts.append(f"Protocol changed from {prot1} to {prot2}")

        return drifts

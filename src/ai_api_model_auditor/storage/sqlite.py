import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, Optional


class SQLiteRepository:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.migrations_dir = Path(__file__).parent / "migrations"

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def apply_migrations(self) -> None:
        """Applies pending database migrations in order."""
        with closing(self._get_connection()) as conn, conn:
            cursor = conn.cursor()

            # Create migration tracking table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS _migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)

            # Get applied migrations
            cursor.execute("SELECT version FROM _migrations")
            applied_versions = {row["version"] for row in cursor.fetchall()}

            # Find and apply new migrations
            migrations = sorted(self.migrations_dir.glob("*.sql"))
            for migration_file in migrations:
                try:
                    version = int(migration_file.stem.split("_")[0])
                except ValueError:
                    continue  # Skip files that don't match the format

                if version not in applied_versions:
                    sql = migration_file.read_text()
                    try:
                        cursor.executescript(sql)
                        cursor.execute(
                            "INSERT INTO _migrations (version) VALUES (?)", (version,)
                        )
                        conn.commit()
                    except sqlite3.Error as e:
                        conn.rollback()
                        raise RuntimeError(
                            f"Failed to apply migration {migration_file.name}: {e}"
                        )

    def save_provider(self, provider_data: Dict[str, Any]) -> None:
        """Saves a provider to the database."""
        with closing(self._get_connection()) as conn, conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO providers (id, name, base_url)
                VALUES (?, ?, ?)
                """,
                (
                    provider_data["id"],
                    provider_data["name"],
                    provider_data["base_url"],
                ),
            )

    def get_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        with closing(self._get_connection()) as conn, conn:
            cursor = conn.execute(
                "SELECT * FROM providers WHERE id = ?", (provider_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def save_provider_model(self, model_data: Dict[str, Any]) -> None:
        """Saves a model to the database."""
        with closing(self._get_connection()) as conn, conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO models (id, provider_id, model_name)
                VALUES (?, ?, ?)
                """,
                (
                    model_data["id"],
                    model_data["provider_id"],
                    model_data["model_name"],
                ),
            )

    def get_provider_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        with closing(self._get_connection()) as conn, conn:
            cursor = conn.execute("SELECT * FROM models WHERE id = ?", (model_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def save_audit_run(self, run_data: Dict[str, Any]) -> None:
        """Saves an audit run to the database."""
        with closing(self._get_connection()) as conn, conn:
            config_json = json.dumps(run_data.get("configuration", {}))
            conn.execute(
                """
                INSERT OR REPLACE INTO audit_runs
                (id, started_at, completed_at, status, configuration)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    run_data["id"],
                    run_data["started_at"],
                    run_data.get("completed_at"),
                    run_data["status"],
                    config_json,
                ),
            )

    def get_audit_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        with closing(self._get_connection()) as conn, conn:
            cursor = conn.execute("SELECT * FROM audit_runs WHERE id = ?", (run_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                if d.get("configuration"):
                    d["configuration"] = json.loads(d["configuration"])
                return d
            return None

    def save_test_case(self, test_case_data: Dict[str, Any]) -> None:
        """Saves a test case to the database."""
        with closing(self._get_connection()) as conn, conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO test_cases
                (id, audit_run_id, name, description, category)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    test_case_data["id"],
                    test_case_data["audit_run_id"],
                    test_case_data["name"],
                    test_case_data.get("description"),
                    test_case_data.get("category"),
                ),
            )

    def get_test_case(self, test_case_id: str) -> Optional[Dict[str, Any]]:
        with closing(self._get_connection()) as conn, conn:
            cursor = conn.execute(
                "SELECT * FROM test_cases WHERE id = ?", (test_case_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def save_observation(self, obs_data: Dict[str, Any]) -> None:
        """Saves an observation to the database."""
        with closing(self._get_connection()) as conn, conn:
            evidence_json = json.dumps(obs_data.get("evidence_data", {}))
            conn.execute(
                """
                INSERT OR REPLACE INTO observations
                (id, test_case_id, model_id, probe_type, evidence_data)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    obs_data["id"],
                    obs_data["test_case_id"],
                    obs_data["model_id"],
                    obs_data["probe_type"],
                    evidence_json,
                ),
            )

    def get_observation(self, obs_id: str) -> Optional[Dict[str, Any]]:
        with closing(self._get_connection()) as conn, conn:
            cursor = conn.execute("SELECT * FROM observations WHERE id = ?", (obs_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                if d.get("evidence_data"):
                    d["evidence_data"] = json.loads(d["evidence_data"])
                return d
            return None

    def save_fingerprint(self, fp_data: Dict[str, Any]) -> None:
        """Saves a fingerprint to the database."""
        with closing(self._get_connection()) as conn, conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO fingerprints
                (id, observation_id, feature_name, feature_value, confidence)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    fp_data["id"],
                    fp_data["observation_id"],
                    fp_data["feature_name"],
                    fp_data["feature_value"],
                    fp_data.get("confidence"),
                ),
            )

    def get_fingerprint(self, fp_id: str) -> Optional[Dict[str, Any]]:
        with closing(self._get_connection()) as conn, conn:
            cursor = conn.execute("SELECT * FROM fingerprints WHERE id = ?", (fp_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def save_score(self, score_data: Dict[str, Any]) -> None:
        """Saves a score to the database."""
        with closing(self._get_connection()) as conn, conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO scores
                (id, audit_run_id, model_id, dimension, score_value)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    score_data["id"],
                    score_data["audit_run_id"],
                    score_data["model_id"],
                    score_data["dimension"],
                    score_data["score_value"],
                ),
            )

    def get_score(self, score_id: str) -> Optional[Dict[str, Any]]:
        with closing(self._get_connection()) as conn, conn:
            cursor = conn.execute("SELECT * FROM scores WHERE id = ?", (score_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def save_cluster(self, cluster_data: Dict[str, Any]) -> None:
        """Saves a cluster to the database."""
        with closing(self._get_connection()) as conn, conn:
            members_json = json.dumps(cluster_data.get("members", []))
            conn.execute(
                """
                INSERT OR REPLACE INTO clusters
                (id, audit_run_id, cluster_name, members)
                VALUES (?, ?, ?, ?)
                """,
                (
                    cluster_data["id"],
                    cluster_data["audit_run_id"],
                    cluster_data["cluster_name"],
                    members_json,
                ),
            )

    def get_cluster(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        with closing(self._get_connection()) as conn, conn:
            cursor = conn.execute("SELECT * FROM clusters WHERE id = ?", (cluster_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                if d.get("members"):
                    d["members"] = json.loads(d["members"])
                return d
            return None

    def save_raw_artifact(self, artifact_data: Dict[str, Any]) -> None:
        """Saves a raw artifact reference to the database."""
        with closing(self._get_connection()) as conn, conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO raw_artifacts
                (id, audit_run_id, artifact_type, storage_path, hash_sha256)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    artifact_data["id"],
                    artifact_data["audit_run_id"],
                    artifact_data["artifact_type"],
                    artifact_data["storage_path"],
                    artifact_data["hash_sha256"],
                ),
            )

    def get_raw_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        with closing(self._get_connection()) as conn, conn:
            cursor = conn.execute(
                "SELECT * FROM raw_artifacts WHERE id = ?", (artifact_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

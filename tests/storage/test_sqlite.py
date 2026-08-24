import sqlite3

import pytest

from ai_api_model_auditor.storage.sqlite import SQLiteRepository


@pytest.fixture
def repo(tmp_path):
    db_path = tmp_path / "test.db"
    repo = SQLiteRepository(str(db_path))
    repo.apply_migrations()
    return repo


def test_migrations_repeatable(tmp_path):
    db_path = tmp_path / "test_mig.db"
    repo = SQLiteRepository(str(db_path))
    repo.apply_migrations()
    # Should not raise an error on second run
    repo.apply_migrations()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='_migrations'"
        )
        assert cursor.fetchone() is not None


def test_save_and_get_provider(repo):
    data = {"id": "prov_1", "name": "Test Provider", "base_url": "https://test.local"}
    repo.save_provider(data)

    fetched = repo.get_provider("prov_1")
    assert fetched is not None
    assert fetched["id"] == "prov_1"
    assert fetched["name"] == "Test Provider"
    assert fetched["base_url"] == "https://test.local"
    assert "created_at" in fetched


def test_save_and_get_provider_model(repo):
    provider_data = {"id": "prov_1", "name": "P1", "base_url": "http://p1"}
    repo.save_provider(provider_data)

    data = {"id": "mod_1", "provider_id": "prov_1", "model_name": "test-model-v1"}
    repo.save_provider_model(data)

    fetched = repo.get_provider_model("mod_1")
    assert fetched is not None
    assert fetched["id"] == "mod_1"
    assert fetched["provider_id"] == "prov_1"
    assert fetched["model_name"] == "test-model-v1"


def test_save_and_get_audit_run(repo):
    data = {
        "id": "run_1",
        "started_at": "2026-08-21T10:00:00Z",
        "status": "RUNNING",
        "configuration": {"param": "value"},
    }
    repo.save_audit_run(data)

    fetched = repo.get_audit_run("run_1")
    assert fetched is not None
    assert fetched["id"] == "run_1"
    assert fetched["status"] == "RUNNING"
    assert fetched["configuration"] == {"param": "value"}
    assert fetched["completed_at"] is None


def test_save_and_get_test_case(repo):
    run_data = {"id": "run_1", "started_at": "now", "status": "RUNNING"}
    repo.save_audit_run(run_data)

    data = {
        "id": "tc_1",
        "audit_run_id": "run_1",
        "name": "Test TC",
        "description": "Desc",
        "category": "cat1",
    }
    repo.save_test_case(data)

    fetched = repo.get_test_case("tc_1")
    assert fetched is not None
    assert fetched["id"] == "tc_1"
    assert fetched["audit_run_id"] == "run_1"
    assert fetched["name"] == "Test TC"


def test_save_and_get_observation(repo):
    # Setup dependencies
    repo.save_provider({"id": "p", "name": "p", "base_url": "u"})
    repo.save_provider_model({"id": "m", "provider_id": "p", "model_name": "m"})
    repo.save_audit_run({"id": "r", "started_at": "now", "status": "OK"})
    repo.save_test_case({"id": "t", "audit_run_id": "r", "name": "t"})

    data = {
        "id": "obs_1",
        "test_case_id": "t",
        "model_id": "m",
        "probe_type": "latency",
        "evidence_data": {"val": 100},
    }
    repo.save_observation(data)

    fetched = repo.get_observation("obs_1")
    assert fetched is not None
    assert fetched["id"] == "obs_1"
    assert fetched["evidence_data"] == {"val": 100}


def test_save_and_get_fingerprint(repo):
    # Setup deps
    repo.save_provider({"id": "p", "name": "p", "base_url": "u"})
    repo.save_provider_model({"id": "m", "provider_id": "p", "model_name": "m"})
    repo.save_audit_run({"id": "r", "started_at": "now", "status": "OK"})
    repo.save_test_case({"id": "t", "audit_run_id": "r", "name": "t"})
    repo.save_observation(
        {
            "id": "o",
            "test_case_id": "t",
            "model_id": "m",
            "probe_type": "p",
            "evidence_data": {},
        }
    )

    data = {
        "id": "fp_1",
        "observation_id": "o",
        "feature_name": "style",
        "feature_value": "formal",
        "confidence": 0.95,
    }
    repo.save_fingerprint(data)

    fetched = repo.get_fingerprint("fp_1")
    assert fetched is not None
    assert fetched["id"] == "fp_1"
    assert fetched["feature_value"] == "formal"
    assert fetched["confidence"] == 0.95


def test_save_and_get_score(repo):
    repo.save_provider({"id": "p", "name": "p", "base_url": "u"})
    repo.save_provider_model({"id": "m", "provider_id": "p", "model_name": "m"})
    repo.save_audit_run({"id": "r", "started_at": "now", "status": "OK"})

    data = {
        "id": "s_1",
        "audit_run_id": "r",
        "model_id": "m",
        "dimension": "safety",
        "score_value": 0.8,
    }
    repo.save_score(data)

    fetched = repo.get_score("s_1")
    assert fetched is not None
    assert fetched["id"] == "s_1"
    assert fetched["score_value"] == 0.8


def test_save_and_get_cluster(repo):
    repo.save_audit_run({"id": "r", "started_at": "now", "status": "OK"})

    data = {
        "id": "c_1",
        "audit_run_id": "r",
        "cluster_name": "OpenAI-like",
        "members": ["m1", "m2"],
    }
    repo.save_cluster(data)

    fetched = repo.get_cluster("c_1")
    assert fetched is not None
    assert fetched["id"] == "c_1"
    assert fetched["members"] == ["m1", "m2"]


def test_save_and_get_raw_artifact(repo):
    repo.save_audit_run({"id": "r", "started_at": "now", "status": "OK"})

    data = {
        "id": "art_1",
        "audit_run_id": "r",
        "artifact_type": "request_log",
        "storage_path": "/tmp/test.json",
        "hash_sha256": "abc123hash",
    }
    repo.save_raw_artifact(data)

    fetched = repo.get_raw_artifact("art_1")
    assert fetched is not None
    assert fetched["id"] == "art_1"
    assert fetched["hash_sha256"] == "abc123hash"

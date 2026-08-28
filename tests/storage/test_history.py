from ai_api_model_auditor.storage.history import HistoryManager


def test_history_manager_save_and_get(tmp_path):
    db_path = str(tmp_path / "test_history.db")
    manager = HistoryManager(db_path=db_path)

    run_data = {
        "provider": "openai",
        "model": "gpt-4",
        "run_date": "2026-08-21",
        "results": {
            "family_confidence": "high",
            "clusters": ["a", "b"],
            "mapping": {"key": "val"},
            "protocol": "http",
        },
    }

    # Save the run
    manager.save_run(run_data)

    # Retrieve without date
    runs = manager.get_history("openai", "gpt-4")
    assert len(runs) == 1
    assert runs[0]["run_date"] == "2026-08-21"

    # Retrieve with specific date
    runs_date = manager.get_history("openai", "gpt-4", date="2026-08-21")
    assert len(runs_date) == 1

    # Retrieve with unknown date
    runs_empty = manager.get_history("openai", "gpt-4", date="1999-01-01")
    assert len(runs_empty) == 0


def test_history_manager_detect_drift():
    manager = HistoryManager(
        ":memory:"
    )  # Drift detection doesn't need DB access strictly, but we init to memory

    run1 = {
        "results": {
            "family_confidence": "high",
            "clusters": ["a"],
            "mapping": {"1": "2"},
            "protocol": "v1",
        }
    }

    run2 = {
        "results": {
            "family_confidence": "medium",
            "clusters": ["a", "b"],
            "mapping": {"1": "3"},
            "protocol": "v2",
        }
    }

    drifts = manager.detect_drift(run1, run2)
    assert len(drifts) == 4
    assert any("Family confidence changed" in d for d in drifts)
    assert any("Clusters changed" in d for d in drifts)
    assert any("Mapping changed" in d for d in drifts)
    assert any("Protocol changed" in d for d in drifts)

    # Identical runs should produce no drift
    drifts_same = manager.detect_drift(run1, run1)
    assert len(drifts_same) == 0

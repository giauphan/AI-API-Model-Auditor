import pytest

from ai_api_model_auditor.storage.history import HistoryManager
from ai_api_model_auditor.storage.replay import Replayer


def test_replayer_replay_run():
    # Create an in-memory manager
    manager = HistoryManager(":memory:")
    replayer = Replayer(history_manager=manager)

    run_data = {
        "provider": "anthropic",
        "model": "claude-3",
        "run_date": "2026-08-22",
        "results": {"evidence": "mocked"},
    }

    result = replayer.replay_run(run_data)

    assert result["status"] == "replayed"
    assert result["provider"] == "anthropic"
    assert result["model"] == "claude-3"
    assert result["original_run_date"] == "2026-08-22"
    assert result["results"]["evidence"] == "mocked"


def test_replayer_invalid_run():
    replayer = Replayer()
    with pytest.raises(ValueError, match="missing provider or model"):
        replayer.replay_run({"run_date": "2026-08-22"})

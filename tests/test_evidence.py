import os
import json
from ai_api_model_auditor.storage.evidence import EvidenceStore
from ai_api_model_auditor.safety import redactor

def test_evidence_store_saves_and_redacts(tmp_path):
    store = EvidenceStore(output_dir=str(tmp_path))
    redactor.add_secret("SUPER_SECRET_TOKEN")

    data = {
        "provider": "test",
        "response": {
            "text": "The key is SUPER_SECRET_TOKEN and sk-1234567890abcdef1234567890abcdef1234",
            "nested": ["SUPER_SECRET_TOKEN", "normal"]
        }
    }

    path = store.save_evidence("test_audit", data)

    assert os.path.exists(path)

    with open(path, "r") as f:
        saved_data = json.load(f)

    saved_text = saved_data["response"]["text"]
    assert "SUPER_SECRET_TOKEN" not in saved_text
    assert "***REDACTED***" in saved_text
    assert "sk-1234" not in saved_text

    saved_nested = saved_data["response"]["nested"]
    assert "SUPER_SECRET_TOKEN" not in saved_nested
    assert "***REDACTED***" in saved_nested

def test_evidence_store_manifest_and_config(tmp_path):
    store = EvidenceStore(output_dir=str(tmp_path))

    # Save a config
    config_data = {"openai_api_key": "sk-1234567890abcdef1234567890abcdef1234", "setting": "value"}
    config_path = store.save_config(config_data)

    assert os.path.exists(config_path)

    # Save evidence
    data = {"test": "data"}
    evidence_path = store.save_evidence("test_manifest", data, metadata={"model": "gpt-4"})

    # Check manifest
    manifest_path = tmp_path / "manifest.json"
    assert manifest_path.exists()

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    assert "artifacts" in manifest
    artifacts = manifest["artifacts"]
    assert len(artifacts) == 2

    # Config entry
    assert artifacts[0]["file"] == "config.redacted.json"
    assert "sha256" in artifacts[0]
    assert artifacts[0]["type"] == "config"

    # Evidence entry
    assert artifacts[1]["file"] == os.path.basename(evidence_path)
    assert "sha256" in artifacts[1]
    assert artifacts[1]["model"] == "gpt-4"

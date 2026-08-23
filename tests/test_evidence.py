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

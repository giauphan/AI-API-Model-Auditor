import pytest
import os
from ai_api_model_auditor.models.auditor import Auditor

def test_evidence_policy_documentation_exists():
    # Use path relative to the test file to find the docs directory
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    doc_path = os.path.join(repo_root, "docs", "evidence-policy.md")

    with open(doc_path, "r") as f:
        content = f.read()

    # Asserting evidence vs inference rules
    assert "Evidence vs. Inference" in content
    assert "never claim exact hidden-model identity with certainty" in content

    # Asserting 15 key questions
    assert "The 15 Key Questions" in content
    assert "evidence strength" in content

def test_auditor_refuses_unsupported_certainty():
    auditor = Auditor()

    with pytest.raises(ValueError, match="Unsupported certainty claim"):
        auditor.claim_model_identity(certainty="DEFINITIVE", evidence_strength="WEAK")

    assert auditor.claim_model_identity(certainty="PROBABLE", evidence_strength="STRONG") == "Claim valid"

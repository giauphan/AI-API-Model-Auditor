import json
import os
import pytest
from typing import Dict, Any

from ai_api_model_auditor.core.pipeline import WAFDetector, IdentityInferencer, EvidenceStore, ReportGenerator


@pytest.fixture
def real_world_fixture() -> Dict[str, Any]:
    fixture_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "fixtures", "first_real_world", "first_fixture.json"
    )
    with open(fixture_path, "r") as f:
        return json.load(f)


def test_waf_failure_handling_and_report_generation(real_world_fixture: Dict[str, Any]):
    """
    Test that a real-world or safely recorded fixture handles WAF failure
    without identity inference, and that successful runs produce the expected
    end-to-end report, verifying safety controls.
    """
    # 1. Initialize Pipeline Components
    detector = WAFDetector()
    inferencer = IdentityInferencer()
    store = EvidenceStore()
    reporter = ReportGenerator()

    # Simulated Request that triggered the fixture response
    mock_request = {
        "headers": {
            "Authorization": "Bearer real_secret_token_123"
        }
    }

    # 2. Evaluate WAF Failure and Identity Inference
    is_waf_failure = detector.analyze_response(real_world_fixture)
    identity = inferencer.infer(real_world_fixture)

    assert is_waf_failure is True, "System must detect WAF failure when status is 403"
    assert identity is None, "System must NOT infer identity on WAF failure"

    # 3. Verify Evidence Processing and Safety Controls
    evidence = store.process(mock_request, real_world_fixture)

    # Check Secret Redaction
    assert evidence["redacted_headers"].get("Authorization") == "[REDACTED]", "Secrets must be redacted in evidence"

    # Check bounded cost and concurrency
    assert evidence.get("cost_bounded") is True, "Run must be cost-bounded"
    assert evidence.get("concurrency_bounded") is True, "Run must be concurrency-bounded"

    # Check separation of concerns
    assert evidence.get("evidence_separated_from_inference") is True, "Evidence must be strictly separated from inference"

    # 4. Verify End-to-End Report Generation
    report_success = reporter.generate(evidence)
    assert report_success is True, "Expected end-to-end report must be generated on successful run"

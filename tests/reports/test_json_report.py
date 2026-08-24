import json

from modelaudit.reports.json import ReportData, generate_json_report


def test_generate_json_report():
    data: ReportData = {
        "target": "openai/gpt-4",
        "connectivity": True,
        "advertised_callable_status": "OK",
        "protocol": "HTTP/1.1",
        "family_confidence": 0.95,
        "suspicion_dimensions": ["token_leakage", "prompt_injection"],
        "strongest_evidence": "Found internal ID",
        "limitations": ["Requires paid account"],
        "artifact_paths": ["/tmp/report1.json", "/tmp/report2.json"],
    }

    result = generate_json_report(data)

    parsed = json.loads(result)

    assert parsed["target"] == "openai/gpt-4"
    assert parsed["connectivity"] is True
    assert parsed["advertised_callable_status"] == "OK"
    assert parsed["protocol"] == "HTTP/1.1"
    assert parsed["family_confidence"] == 0.95
    assert parsed["suspicion_dimensions"] == ["token_leakage", "prompt_injection"]
    assert parsed["strongest_evidence"] == "Found internal ID"
    assert parsed["limitations"] == ["Requires paid account"]
    assert parsed["artifact_paths"] == ["/tmp/report1.json", "/tmp/report2.json"]


def test_generate_json_report_empty():
    data: ReportData = {}
    result = generate_json_report(data)
    parsed = json.loads(result)
    assert parsed == {}

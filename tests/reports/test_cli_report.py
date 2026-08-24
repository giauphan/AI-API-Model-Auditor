from modelaudit.reports.cli import generate_cli_report
from modelaudit.reports.json import ReportData


def test_generate_cli_report():
    data: ReportData = {
        "target": "anthropic/claude-3",
        "connectivity": True,
        "advertised_callable_status": "Online",
        "protocol": "HTTPS",
        "family_confidence": 0.99,
        "suspicion_dimensions": ["latency", "censorship"],
        "strongest_evidence": "Latency spike",
        "limitations": ["Rate limited"],
        "artifact_paths": ["/var/log/audit.log"],
    }

    result = generate_cli_report(data)

    assert "=== Model Audit Report ===" in result
    assert "Target: anthropic/claude-3" in result
    assert "Connectivity: True" in result
    assert "Advertised/Callable Status: Online" in result
    assert "Protocol: HTTPS" in result
    assert "Family Confidence: 0.99" in result
    assert "Suspicion Dimensions: latency, censorship" in result
    assert "Strongest Evidence: Latency spike" in result
    assert "Limitations: Rate limited" in result
    assert "Artifact Paths:" in result
    assert "- /var/log/audit.log" in result


def test_generate_cli_report_missing_fields():
    data: ReportData = {"target": "local/model"}

    result = generate_cli_report(data)

    assert "Target: local/model" in result
    assert "Connectivity: False" in result
    assert "Advertised/Callable Status: Unknown" in result
    assert "Protocol: Unknown" in result
    assert "Family Confidence: Unknown" in result
    assert "Suspicion Dimensions: None" in result
    assert "Strongest Evidence: None" in result
    assert "Limitations: None" in result
    assert "Artifact Paths: None" in result


def test_generate_cli_report_dict_dimensions():
    data: ReportData = {
        "target": "gemini/pro",
        "suspicion_dimensions": {"bias": "high", "toxicity": "low"},
    }

    result = generate_cli_report(data)
    assert "Suspicion Dimensions: bias: high, toxicity: low" in result

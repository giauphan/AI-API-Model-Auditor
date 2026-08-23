from modelaudit.dashboard.app import generate_dashboard
from modelaudit.reports.html import HTMLReporter


def test_html_report_sections_present():
    reporter = HTMLReporter()
    mock_data = {
        "overview": {"status": "ok"},
        "providers": {"openai": "ok"},
        "models": {"gpt-4": "ok"},
        "runs": {"run-1": "ok"},
        "comparison": {"diff": 0},
        "rotation_clusters": {"c1": "ok"},
        "raw_artifacts": {"art1": "ok"},
        "evidence": {"ev1": "ok"},
        "history": {"hist1": "ok"},
        "similarity_matrices": {"sim1": "ok"},
    }

    html = reporter.generate_report(mock_data)

    # Assert all expected sections are present
    assert "<div id='overview'>" in html
    assert "<div id='providers'>" in html
    assert "<div id='models'>" in html
    assert "<div id='runs'>" in html
    assert "<div id='comparison'>" in html
    assert "<div id='rotation_clusters'>" in html
    assert "<div id='raw_artifacts'>" in html
    assert "<div id='evidence'>" in html
    assert "<div id='history'>" in html
    assert "<div id='similarity_matrices'>" in html


def test_html_secret_redaction():
    reporter = HTMLReporter()
    mock_data = {
        "similarity_matrices": {
            "matrix1": "sk-1234567890abcdef",
            "nested": {"key": "sk-abcdef1234567890", "normal": "hello world"},
        },
        "raw_artifacts": ["sk-secret123", "public info"],
    }

    html = reporter.generate_report(mock_data)

    # Assert secrets are redacted
    assert "sk-1234567890abcdef" not in html
    assert "sk-abcdef1234567890" not in html
    assert "sk-secret123" not in html
    assert "[REDACTED_SECRET]" in html

    # Assert normal data is still present
    assert "hello world" in html
    assert "public info" in html


def test_dashboard_generation():
    mock_data = {
        "overview": {"status": "dashboard_ok"},
        "raw_artifacts": {"secret_key": "sk-dashboard123"},
    }

    dashboard_html = generate_dashboard(mock_data)

    assert "<div class='dashboard-widget' id='dashboard_overview'>" in dashboard_html
    assert "dashboard_ok" in dashboard_html
    assert "sk-dashboard123" not in dashboard_html
    assert "[REDACTED_SECRET]" in dashboard_html

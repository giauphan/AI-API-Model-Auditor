import logging

from modelaudit.integrations.header_audit import HeaderAuditor


def test_record_headers_redaction():
    auditor = HeaderAuditor()
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer secret-token",
        "x-api-key": "my-secret-key",
        "anthropic-version": "2023-06-01",
        "User-Agent": "python-requests/2.31.0",
        "Accept": "*/*",
    }

    auditor.record_headers("before_routing", headers)
    recorded = auditor.recorded_headers["before_routing"]

    assert recorded["Content-Type"] == "application/json"
    assert recorded["Accept"] == "*/*"

    assert recorded["Authorization"] == "***REDACTED***"
    assert recorded["x-api-key"] == "***REDACTED***"
    assert recorded["anthropic-version"] == "***REDACTED***"
    assert recorded["User-Agent"] == "***REDACTED***"


def test_detect_override_warning(caplog):
    auditor = HeaderAuditor()
    baseline = {
        "Authorization": "Bearer initial-token",
        "Content-Type": "application/json",
    }
    current = {"Authorization": "Bearer new-token", "Content-Type": "application/json"}

    with caplog.at_level(logging.WARNING):
        auditor.detect_override(baseline, current)

    assert (
        "Header override detected for sensitive header: 'Authorization'" in caplog.text
    )
    assert "initial-token" not in caplog.text
    assert "new-token" not in caplog.text


def test_detect_override_no_warning_when_same(caplog):
    auditor = HeaderAuditor()
    baseline = {
        "Authorization": "Bearer initial-token",
    }
    current = {
        "Authorization": "Bearer initial-token",
    }

    with caplog.at_level(logging.WARNING):
        auditor.detect_override(baseline, current)

    assert caplog.text == ""


def test_detect_override_non_sensitive_changed(caplog):
    auditor = HeaderAuditor()
    baseline = {
        "Content-Type": "application/json",
    }
    current = {
        "Content-Type": "application/xml",
    }

    with caplog.at_level(logging.WARNING):
        auditor.detect_override(baseline, current)

    assert caplog.text == ""


def test_record_multiple_stages():
    auditor = HeaderAuditor()
    auditor.record_headers("before_routing", {"x-api-key": "key1"})
    auditor.record_headers("emitted", {"x-api-key": "key2"})
    auditor.record_headers("downstream", {"x-api-key": "key3"})

    assert "before_routing" in auditor.recorded_headers
    assert "emitted" in auditor.recorded_headers
    assert "downstream" in auditor.recorded_headers

    assert auditor.recorded_headers["before_routing"]["x-api-key"] == "***REDACTED***"
    assert auditor.recorded_headers["emitted"]["x-api-key"] == "***REDACTED***"
    assert auditor.recorded_headers["downstream"]["x-api-key"] == "***REDACTED***"

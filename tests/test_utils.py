from ai_api_model_auditor.utils import SecretRedactor


def test_secret_redactor_string() -> None:
    redactor = SecretRedactor(secrets={"super-secret-key"})

    text = "Here is my key: super-secret-key. Do not share."
    redacted = redactor.redact_string(text)

    assert "super-secret-key" not in redacted
    assert "***REDACTED***" in redacted


def test_secret_redactor_add_secret() -> None:
    redactor = SecretRedactor(secrets=set())
    redactor.add_secret("another-secret")

    text = "Key: another-secret"
    assert redactor.redact_string(text) == "Key: ***REDACTED***"


def test_secret_redactor_too_short() -> None:
    # secrets that are 3 chars or less should be ignored to prevent over-redaction
    redactor = SecretRedactor(secrets={"abc"})
    assert redactor.redact_string("abcdef") == "abcdef"


def test_secret_redactor_data() -> None:
    redactor = SecretRedactor(secrets={"secret123"})

    data = {
        "headers": {"Authorization": "Bearer secret123"},
        "items": ["public-item", "hidden-secret123-item"],
    }

    redacted_data = redactor.redact_data(data)

    assert redacted_data["headers"]["Authorization"] == "Bearer ***REDACTED***"
    assert redacted_data["items"][1] == "hidden-***REDACTED***-item"
    assert redacted_data["items"][0] == "public-item"

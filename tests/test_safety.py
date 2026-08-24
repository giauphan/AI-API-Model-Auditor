from ai_api_model_auditor.safety import SecretRedactor

def test_secret_redactor_explicit_secret():
    redactor = SecretRedactor()
    redactor.add_secret("my-super-secret-key")
    text = "Here is my-super-secret-key in some text."
    redacted = redactor.redact(text)
    assert "***REDACTED***" in redacted
    assert "my-super-secret-key" not in redacted

def test_secret_redactor_regex_openai():
    redactor = SecretRedactor()
    text = "My key is sk-1234567890abcdef1234567890abcdef1234"
    redacted = redactor.redact(text)
    assert "***REDACTED***" in redacted
    assert "sk-" not in redacted

def test_secret_redactor_regex_anthropic():
    redactor = SecretRedactor()
    text = "My key is sk-ant-api03-1234567890abcdef-123"
    redacted = redactor.redact(text)
    assert "***REDACTED***" in redacted
    assert "sk-ant-" not in redacted

def test_secret_redactor_regex_bearer():
    redactor = SecretRedactor()
    text = "Header: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
    redacted = redactor.redact(text)
    assert "Bearer ***REDACTED***" in redacted
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in redacted

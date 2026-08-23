from typing import Any, Set


class SecretRedactor:
    """
    Utility to redact sensitive information such as API keys from
    strings and structured data (dictionaries/lists).
    """

    def __init__(self, secrets: Set[str], replacement: str = "***REDACTED***"):
        """
        Initialize with a set of secrets to redact.
        """
        # Filter out empty or very short secrets to avoid over-redaction
        self.secrets = {s for s in secrets if s and len(s) > 3}
        self.replacement = replacement

    def add_secret(self, secret: str) -> None:
        """Add a new secret to the redactor."""
        if secret and len(secret) > 3:
            self.secrets.add(secret)

    def redact_string(self, text: str) -> str:
        """Redact known secrets from a string."""
        if not text or not self.secrets:
            return text

        redacted_text = text
        for secret in self.secrets:
            # Simple replace, as regex might fail on special chars in secrets
            # Note: order could matter if one secret is a substring of another,
            # but simple replace is usually sufficient for keys.
            redacted_text = redacted_text.replace(secret, self.replacement)
        return redacted_text

    def redact_data(self, data: Any) -> Any:
        """
        Recursively redact secrets from a data structure (dict, list, etc).
        Useful for cleaning JSON responses before saving/logging evidence.
        """
        if not self.secrets:
            return data

        if isinstance(data, dict):
            return {k: self.redact_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.redact_data(v) for v in data]
        elif isinstance(data, str):
            return self.redact_string(data)
        return data

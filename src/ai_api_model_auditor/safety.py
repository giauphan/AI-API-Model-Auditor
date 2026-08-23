import re
import time
from typing import Set

_REDACTED_STR = "***REDACTED***"

class SecretRedactor:
    def __init__(self):
        self._secrets: Set[str] = set()

    def add_secret(self, secret: str):
        if secret and len(secret) > 4: # Don't redact tiny strings
            self._secrets.add(secret)

    def redact(self, text: str) -> str:
        if not text:
            return text

        redacted_text = text
        for secret in self._secrets:
            # Simple string replacement for exact matches
            redacted_text = redacted_text.replace(secret, _REDACTED_STR)

            # Also try to replace URL encoded or slightly mangled versions if needed,
            # but simple replace is usually enough for logs/evidence.

        # Regex patterns for common API keys if they weren't explicitly added
        # OpenAI
        redacted_text = re.sub(r'sk-[a-zA-Z0-9]{32,}', _REDACTED_STR, redacted_text)
        # Anthropic (sk-ant-...)
        redacted_text = re.sub(r'sk-ant-[a-zA-Z0-9_-]+', _REDACTED_STR, redacted_text)
        # Common bearer tokens
        redacted_text = re.sub(r'Bearer\s+[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+', f'Bearer {_REDACTED_STR}', redacted_text)

        return redacted_text

# Global redactor instance
redactor = SecretRedactor()

def redact_string(text: str) -> str:
    return redactor.redact(text)

class RateLimiter:
    def __init__(self, delay_seconds: float):
        self.delay_seconds = delay_seconds
        self.last_call_time = 0.0

    def wait(self):
        now = time.time()
        elapsed = now - self.last_call_time
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self.last_call_time = time.time()

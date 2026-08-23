import logging
from typing import Dict, Literal

logger = logging.getLogger(__name__)


class HeaderAuditor:
    """
    Audits and records HTTP headers at various stages of routing, ensuring sensitive
    information is redacted and overrides are detected without leaking secrets.
    """

    SENSITIVE_HEADERS = {
        "authorization",
        "x-api-key",
        "anthropic-version",
        "user-agent",
    }

    def __init__(self):
        self.recorded_headers: Dict[str, Dict[str, str]] = {}

    def _redact_value(self, key: str, value: str) -> str:
        """Redacts sensitive header values."""
        if key.lower() in self.SENSITIVE_HEADERS:
            return "***REDACTED***"
        return value

    def record_headers(
        self,
        stage: Literal["before_routing", "emitted", "downstream"],
        headers: Dict[str, str],
    ) -> None:
        """
        Records headers for a specific stage, redacting sensitive values.

        Args:
            stage: The stage at which headers are recorded ("before_routing",
                "emitted", "downstream").
            headers: A dictionary of header keys and values.
        """
        redacted = {k: self._redact_value(k, v) for k, v in headers.items()}
        self.recorded_headers[stage] = redacted

    def detect_override(
        self, baseline_headers: Dict[str, str], current_headers: Dict[str, str]
    ) -> None:
        """
        Detects if sensitive headers have been overridden between a baseline and
        current state. Emits a warning without exposing the actual values.

        Args:
            baseline_headers: The initial headers.
            current_headers: The subsequent headers that might have overridden the
                baseline.
        """
        baseline_keys = {k.lower(): k for k in baseline_headers.keys()}

        for curr_key, curr_val in current_headers.items():
            curr_key_lower = curr_key.lower()

            if curr_key_lower in self.SENSITIVE_HEADERS:
                if curr_key_lower in baseline_keys:
                    baseline_key = baseline_keys[curr_key_lower]
                    if baseline_headers[baseline_key] != curr_val:
                        logger.warning(
                            f"Header override detected for sensitive header: "
                            f"'{curr_key}'. Original and new values have been redacted."
                        )

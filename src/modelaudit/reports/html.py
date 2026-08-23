import html
import json
import re
from typing import Any, Dict


class HTMLReporter:
    """Generates HTML reports from audit data."""

    def __init__(self) -> None:
        pass

    def redact_secrets(self, text: str) -> str:
        """Redact secrets like API keys from strings."""
        if not isinstance(text, str):
            return text
        # Simple regex for generic API keys starting with sk-
        # and arbitrary lengths of word chars/hyphens
        pattern = re.compile(r"sk-[a-zA-Z0-9\-_]+")
        return pattern.sub("[REDACTED_SECRET]", text)

    def sanitize_data(self, data: Any) -> Any:
        """Recursively sanitizes a data structure to redact secrets."""
        if isinstance(data, dict):
            return {k: self.sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        elif isinstance(data, str):
            return self.redact_secrets(data)
        else:
            return data

    def generate_report(self, data: Dict[str, Any]) -> str:
        """
        Constructs an HTML string containing the required sections:
        overview, providers, models, runs, comparison, rotation clusters,
        raw artifacts, evidence, history, and similarity matrices.
        """
        sanitized_data = self.sanitize_data(data)

        # Simple HTML string building since we can't guarantee Jinja2
        # is on the project without pyproject.toml.
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head><title>AI API Model Audit Report</title></head>",
            "<body>",
            "<h1>AI API Model Audit Report</h1>",
        ]

        sections = [
            "overview",
            "providers",
            "models",
            "runs",
            "comparison",
            "rotation clusters",
            "raw artifacts",
            "evidence",
            "history",
            "similarity matrices",
        ]

        for section in sections:
            section_id = section.replace(" ", "_")
            html_parts.append(f"<div id='{section_id}'>")
            html_parts.append(f"<h2>{section.title()}</h2>")

            section_data = sanitized_data.get(section_id, {})
            if section_data:
                dumped = json.dumps(section_data, indent=2, default=str)

                escaped = html.escape(dumped)
                html_parts.append(f"<pre>{escaped}</pre>")
            else:
                html_parts.append("<p>No data available for this section.</p>")

            html_parts.append("</div>")

        html_parts.append("</body></html>")
        return "\n".join(html_parts)

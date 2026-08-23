import html
import json
from typing import Any, Dict

from modelaudit.reports.html import HTMLReporter


def generate_dashboard(data: Dict[str, Any]) -> str:
    """
    Builds the optional dashboard view reusing HTML components.
    """
    reporter = HTMLReporter()
    sanitized_data = reporter.sanitize_data(data)

    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head><title>Audit Dashboard</title></head>",
        "<body>",
        "<h1>Audit Dashboard</h1>",
        "<div class='dashboard-container'>",
    ]

    # We can reuse the same sections but wrap them in dashboard-style components
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
        html_parts.append(f"<div class='dashboard-widget' id='dashboard_{section_id}'>")
        html_parts.append(f"<h3>{section.title()}</h3>")

        section_data = sanitized_data.get(section_id, {})
        if section_data:

            dumped = json.dumps(section_data, indent=2, default=str)

            escaped = html.escape(dumped)
            html_parts.append(f"<pre>{escaped}</pre>")
        else:
            html_parts.append("<p>No data</p>")

        html_parts.append("</div>")

    html_parts.append("</div>")
    html_parts.append("</body></html>")
    return "\n".join(html_parts)

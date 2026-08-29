import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any

# Simple inline redactor to satisfy secret redaction without depending on unmerged Group 1 code
class SecretRedactor:
    def __init__(self):
        self._secrets = set()

    def add_secret(self, secret: str):
        if secret and len(secret) > 4:
            self._secrets.add(secret)

    def redact(self, text: str) -> str:
        if not text:
            return text
        redacted_text = text
        for secret in self._secrets:
            redacted_text = redacted_text.replace(secret, "***REDACTED***")
        redacted_text = re.sub(r'sk-[a-zA-Z0-9]{32,}', '***REDACTED***', redacted_text)
        return redacted_text

redactor = SecretRedactor()

def redact_string(text: str) -> str:
    return redactor.redact(text)

def sanitize_data(data: Any) -> Any:
    if isinstance(data, str):
        return redact_string(data)
    elif isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(i) for i in data]
    return data

def check_constraint(content: str, constraint: str) -> bool:
    if constraint == "word_count_3":
        words = [w for w in content.strip().split() if w]
        return len(words) == 3
    return False

def check_verbosity(content: str) -> str:
    # Example verbosity check: > 100 words is considered verbose
    words = content.split()
    if len(words) > 100:
        return "verbose"
    elif len(words) > 20:
        return "moderate"
    return "concise"

def run_reasoning_probes(adapter, models: List[str], cases_path: str = "benchmark_packs/reasoning/cases.json") -> List[Dict[str, Any]]:
    """
    Runs reasoning probes against provided models.
    adapter: Should provide get_provider_name() and chat(model, messages).
    cases_path: Optional path to the cases JSON file.
    """
    cases_path_obj = Path(cases_path)
    if not cases_path_obj.exists():
        raise FileNotFoundError(f"Cases file not found at {cases_path_obj}")

    with open(cases_path_obj, "r", encoding="utf-8") as f:
        cases = json.load(f)

    all_findings = []

    for model in models:
        for case in cases:
            finding = {
                "probe": "reasoning",
                "provider": adapter.get_provider_name(),
                "model": model,
                "case_name": case["name"],
                "status": "error",
                "evidence": None
            }

            try:
                # Initial request
                messages = [{"role": "user", "content": case["prompt"]}]
                response = adapter.chat(model, messages)
                content = response.get("content", "")

                passed = False
                if "expected_content_contains" in case:
                    passed = case["expected_content_contains"].lower() in content.lower()
                elif "expected_constraint" in case:
                    passed = check_constraint(content, case["expected_constraint"])

                # Self-correction check if initial fails
                self_correction_triggered = False
                self_correction_passed = False
                correction_content = ""

                if not passed:
                    self_correction_triggered = True
                    messages.append({"role": "assistant", "content": content})
                    messages.append({"role": "user", "content": "Are you sure? Please review your answer and correct it if necessary."})

                    correction_response = adapter.chat(model, messages)
                    correction_content = correction_response.get("content", "")

                    if "expected_content_contains" in case:
                        self_correction_passed = case["expected_content_contains"].lower() in correction_content.lower()
                    elif "expected_constraint" in case:
                        self_correction_passed = check_constraint(correction_content, case["expected_constraint"])

                    if self_correction_passed:
                        passed = True
                        finding["status"] = "pass_after_correction"
                    else:
                        finding["status"] = "fail"
                else:
                    finding["status"] = "pass"

                finding["evidence"] = {
                    "prompt": case["prompt"],
                    "initial_response": content,
                    "initial_verbosity": check_verbosity(content),
                    "self_correction_triggered": self_correction_triggered,
                }

                if self_correction_triggered:
                    finding["evidence"]["correction_response"] = correction_content
                    finding["evidence"]["correction_verbosity"] = check_verbosity(correction_content)

            except Exception as e:
                finding["status"] = "error"
                finding["evidence"] = {"error": str(e)}

            # Apply secret redaction
            finding["evidence"] = sanitize_data(finding["evidence"])
            all_findings.append(finding)

    return all_findings

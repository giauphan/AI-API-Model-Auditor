# Fingerprint Benchmark v1

This benchmark pack contains canaries for evaluating and cross-comparing model behavior across different semantic features.

## Minimized Content

The benchmark content has been minimized to only contain essential prompts required to measure the following capability profiles:
- Multilingual
- Logic
- Tool use
- JSON generation
- Code generation
- Long-context processing

## Leakage Controls

To avoid data leakage and prevent triggering WAF or DLP rules:
- Prompts use abstract, generic examples.
- No Personally Identifiable Information (PII) is included.
- No proprietary API keys, credentials, or sensitive code logic are used.
- The datasets avoid referencing internal company systems or known sensitive domains.

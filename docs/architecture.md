# Architecture Overview

## Objective
The AI API Model Auditor uses an adapter pattern to uniformly interact with various AI model providers (OpenAI, Anthropic, Gemini, etc.) while capturing raw evidence of the transaction and safeguarding secrets.

## Configuration
We use `pydantic` (V2) to enforce typed configuration loading. To protect credentials:
- **API Keys are not serialized:** Configuration schemas only hold the **environment variable name** that contains the API key (e.g. `api_key_env_var`).
- The actual key is dynamically fetched from the environment at runtime using a property `api_key`.

## Adapters
All AI adapters must extend the `BaseModelAdapter` class. Key rules:
1. **Synchronous Networking:** We use a synchronous `httpx.Client()` to orchestrate API calls.
2. **Context Management:** Clients are closed properly using context managers (the `with` statement).
3. **Evidence vs Inference:** The `generate()` method enforces returning both raw HTTP/transaction data (`evidence`) and the parsed result (`inference`). This ensures auditable traces are always preserved.

## Security (Secret Redaction)
A global `SecretRedactor` is employed to intercept any evidence structures before they are logged or written to disk. All known API keys are dynamically added to this redactor to ensure they are masked as `***REDACTED***` in the output.

# AI-API-Model-Auditor

Foundation package for auditing AI API Endpoints.
This is the MVP containing basic configuration, recon, adapters, and evidence preservation functionalities.

## Installation

You can install the auditor locally in editable mode.
Python 3.11+ is recommended.

```bash
pip install -e .
```

To install dev dependencies (for testing):

```bash
pip install -e .[dev]
```

## Setup

The CLI automatically reads standard environment variables for API keys.
Alternatively, you can provide custom base URLs.

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="AIza..."
```

## Usage

You can use the module directly via `python -m ai_api_model_auditor.cli` or via the installed script `ai-auditor` if your `PATH` is configured properly.

### Reconnaissance

Enumerate available models for a provider:

```bash
ai-auditor recon --provider openai
```

Dry-run mode:
```bash
ai-auditor --dry-run recon --provider anthropic
```

### Auditing

Run a basic chat probe against a specific model. Responses and prompts are automatically captured in structured JSON format in the `evidence/` directory.

```bash
ai-auditor audit --provider openai --model gpt-3.5-turbo --prompt "Tell me a joke."
```

Secrets (API keys, common token formats) are automatically redacted in the standard output and evidence files.

## Running Tests

To verify the installation and core functionalities:

```bash
pytest
```

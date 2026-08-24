# Getting Started with AI-API-Model-Auditor

## Prerequisites

Python 3.11+ is recommended.
The CLI relies on standard environment variables for authenticating with various providers.

## Configuration

Set the API keys for the providers you intend to audit:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="AIza..."
```

## Basic Usage

The primary interface is the `ai-auditor` CLI. It supports two main commands for the foundational MVP:

### 1. Reconnaissance

Discover which models are available for a given provider:

```bash
ai-auditor recon --provider openai
```

### 2. Auditing

Run a minimal end-to-end chat probe against a target model. Responses, prompts, and potential errors are saved securely in the `evidence/` directory. Secrets will be automatically redacted.

```bash
ai-auditor audit --provider openai --model gpt-3.5-turbo --prompt "hello, are you functional?"
```

## Dry Run Mode

You can test the CLI mechanics without making real API calls or spending credits by appending `--dry-run`:

```bash
ai-auditor --dry-run recon --provider anthropic
ai-auditor --dry-run audit --provider gemini --model gemini-pro --prompt "test"
```

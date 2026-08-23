# Evidence Policy

This document defines the final design rules for the AI API Model Auditor regarding the 15 key questions it must answer.

## Policy Rules

### 1. Key-Question Coverage
The auditor is designed to answer a specific set of 15 key questions about an AI model's API surface, constraints, behavior, and cost structure.

### 2. Known vs. Inferred
A strict separation must be maintained between what is **known** (empirically tested, documented, or proven) and what is **inferred** (guessed, modeled, or assumed).
- Structured evidence outputs must explicitly tag claims as either `known` or `inferred`.

### 3. Evidence Strength
For every key question answered, the auditor must provide an `evidence_strength` rating (e.g., `strong`, `moderate`, `weak`, or `none`).
- `strong`: Backed by reproducible API tests and definitive documentation.
- `moderate`: Supported by partial tests or secondary documentation.
- `weak`: Based primarily on inference or incomplete data.
- `none`: No evidence available.

### 4. Refusal of Unsupported Certainty Claims
The auditor must explicitly refuse to make certainty claims without adequate evidence.
- If a question cannot be answered with at least a `weak` evidence strength, the auditor must return an `UnsupportedClaim` refusal.
- The auditor must never hallucinate certainty where only inference exists.

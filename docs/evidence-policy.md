# Evidence Policy

This document defines the core principles of evidence handling within the AI API Model Auditor.

## Evidence vs. Inference
- **What is known (Direct Observations):** Raw protocol responses, header bytes, network latencies, explicit HTTP status codes, chunk boundaries, and token structures directly observed on the wire.
- **What is inferred:** Confidence in model family, semantic alignment, behavior profiles, suspicion of WAF injection, or proxy clustering.

The auditor must **never claim exact hidden-model identity with certainty** unless it is mathematically proven (which is rare). It produces confidence levels backed by technical evidence.

## The 15 Key Questions
The Auditor attempts to answer the following 15 key questions:
1. Is the endpoint conforming to the stated OpenAI/Anthropic/Gemini protocol?
2. Are error structures mapped accurately to known upstream behaviors?
3. How does the context window behave under saturation?
4. What are the tokenization boundaries observed via logprobs or chunking?
5. Does the endpoint support streaming appropriately?
6. Are function-calling/tool-use schemas supported natively?
7. Is there a detectable WAF or intermediary proxy modifying the request?
8. Do headers leak clues about the underlying infrastructure?
9. Can hidden system prompts or pre-fill behaviors be fingerprinted?
10. Are specific semantic or style "canary" features present?
11. Is the knowledge cutoff date consistent with claimed models?
12. How does latency scale with input token volume?
13. Does the API honor seeds, temperature, and other configuration parameters?
14. Does the endpoint attempt to self-report an identity that contradicts structural evidence?
15. Is there rotation across distinct underlying models per request?

Every answer must be accompanied by an **evidence strength** level (e.g., NONE, WEAK, STRONG, DEFINITIVE).

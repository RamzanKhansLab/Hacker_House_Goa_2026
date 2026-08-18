# Guardrails

| Case | Decision | User-facing behavior |
| --- | --- | --- |
| Unsafe pattern | `UNSAFE` | “I can't help with that request.” |
| Prompt injection pattern | `INJECTION_BLOCKED` | no retrieved instructions are executed |
| Ambiguous or weak retrieval | `INSUFFICIENT_CONTEXT` | knowledge-base insufficiency message |
| Unsupported generated claim | `INSUFFICIENT_CONTEXT`, `grounded=false` | grounded fallback and sources if available |

The generated answer has a context-only system instruction and retrieved text is explicitly untrusted data. Deterministic validation checks sentence claims against context terms before return. This is a mitigation, not a proof of factual correctness; tune thresholds using held-out data and add domain-specific policy patterns before a production deployment.

# RAG pipeline

1. Validate and normalize query whitespace.
2. Detect a likely script/language and classify unsafe, injection, ambiguous, or normal intent using local rules.
3. Retrieve dense and lexical candidates in parallel, apply RRF and reranking.
4. Stop with `INSUFFICIENT_CONTEXT` if evidence is too weak.
5. Deduplicate and budget context.
6. Generate only from context using a provider-specific adapter.
7. Compare answer claims with context tokens; return a grounded fallback if support fails.
8. Format sources, guardrail decision and individual latency fields.

Each stage has structured inputs/outputs in code rather than a single unbounded `llm(prompt)` call. The voice route adds STT before the same pipeline and sets `stt_ms` independently.

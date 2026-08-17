# Harness and reliability

`RAGOrchestrator` composes input analysis, retrieval, reranking, context construction, generation, grounding, source formatting, cache, and concurrency limits. STT and the OpenAI-compatible LLM use finite two-attempt policies: permanent client failures are not retried; transient timeouts, overloads, and rate limits receive one jittered backoff attempt.

All external provider paths have timeouts (`STT_TIMEOUT_SECONDS`, `LLM_TIMEOUT_SECONDS`, `VECTOR_DB_TIMEOUT_SECONDS`). Qdrant is an adapter and can be swapped for the local index. No network call is made by query routing or guardrails.

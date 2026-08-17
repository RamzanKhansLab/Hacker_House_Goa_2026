# Latency methodology

The `<200 ms` objective applies to the RAG path after text is received: preprocessing, embedding, dense retrieval, BM25, fusion, reranking, context construction, generation, and grounding. It does **not** include a remote speech-to-text call.

Responses expose `stt_ms`, `rag_total_ms`, and `end_to_end_ms`; the frontend renders the speech value separately. `python -m evaluation.benchmark --queries 100` produces P50, P70, P90, P95, P99, and P100 for every available stage on the current machine, warm configuration, model, and index. No measured number is committed as a template.

The main controls are precomputed indexes, one-time model loading, bounded top-k/context, parallel retrieval, cache limits, provider timeouts, and small candidate sets. Report hardware, data subset, provider/model, warm/cold state, and query count beside any submitted results.

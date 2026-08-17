# Architecture

## Request lifecycle

```mermaid
sequenceDiagram
  participant U as Browser
  participant A as API
  participant S as STT
  participant R as RAG harness
  participant V as Vector/BM25 index
  participant L as LLM
  U->>A: typed query or audio upload
  A->>S: audio only, if applicable
  A->>R: normalized query
  R->>R: language + safety + injection analysis
  R->>V: dense and BM25 retrieval in parallel
  R->>R: RRF, rerank, deduplicate, budget context
  R->>L: context-only prompt
  R->>R: deterministic grounding validation
  R-->>A: sources, guardrail status, timings
  A-->>U: structured JSON
```

`RAGOrchestrator` owns the pipeline boundary. Provider adapters implement replaceable STT, embedding, LLM, and vector-store capabilities. Startup only loads a persisted local index or the tiny bundled demo corpus; offline ingestion owns download and embedding.

Failure paths are bounded: invalid media gets a 400 response, unsafe/injection queries are withheld before retrieval, weak retrieval never reaches the LLM, and transient Sarvam/LLM failures receive one retry with backoff before a structured service error. The local rate limiter and request semaphore protect a single free-tier instance; neither is distributed.

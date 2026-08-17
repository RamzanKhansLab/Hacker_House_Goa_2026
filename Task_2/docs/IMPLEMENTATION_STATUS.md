# Implementation status

Last updated: 2026-08-17 (local checkout).

| Feature | Status | Evidence / limitation |
| --- | --- | --- |
| Dataset ingestion commands | IMPLEMENTED | Full MSMARCO-XI ingestion not run: optional `datasets` dependency and representative corpus preparation remain required. |
| Demo index and safe manifest | PASS | Generated locally from 3 multilingual demo documents; [manifest](../data/demo/index_manifest.json) contains no credentials. |
| Chunking, dense, BM25, hybrid, reranking, context | PASS | Covered by unit/integration tests; 17 tests passed. |
| LLM generation, grounding, guardrails | PASS (demo) | Deterministic mock provider covered by tests. Live LLM verification requires credentials. |
| Sarvam STT adapter | CONFIG REQUIRED | Mock STT integration passed. No `SARVAM_API_KEY` is configured, so no live request was sent. |
| Qdrant adapter | CONFIG REQUIRED | No `QDRANT_URL`/`QDRANT_API_KEY` is configured, so no live collection check was sent. |
| Frontend | PASS | `npm run lint` and `npm run build` passed after lockfile synchronization and restoring Vite `index.html`. |
| Backend tests | PASS | `17 passed` with Python 3.10.9; project packaging correctly requires Python 3.11+, which is unavailable on this host. |
| Ruff / MyPy | PASS | `ruff check .` and `mypy app ingestion evaluation` passed. |
| API health/readiness | PASS (in-process) | FastAPI integration tests verified `/health`, `/ready`, query, and voice endpoints in demo mode. |
| Docker build | NOT RUN | Docker CLI is not installed on this host. |
| Render deployment and live probes | NOT RUN | No Render account/service access or hosted URL was supplied. |
| Latency benchmark | PASS (demo only) | 100 warm local requests: RAG P50 0.593 ms, P70 0.626 ms, P100 3.755 ms. See `evaluation_results/LATENCY_REPORT.md`. |
| Retrieval quality comparison | NOT RUN (representative corpus) | The demo corpus achieved MRR/Recall@1 1.0, but it is not a valid MSMARCO-XI comparison. Run a labelled MSMARCO-XI evaluation matrix before submission. |

No deployment, real-provider, full-corpus-quality, or Docker result is claimed without direct verification.

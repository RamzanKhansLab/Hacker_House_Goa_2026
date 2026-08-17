# Free-tier operations

Use the deterministic demo index while developing and a prepared small/representative production index or hosted Qdrant when deploying. Bound `TOP_K`, `RERANK_TOP_K`, context tokens, audio size, rate limit, cache size, and concurrent requests. Avoid full dataset downloads, model downloads, or embedding generation at web-service startup.

Free services can sleep and have limited CPU/RAM. Load one embedding model/index per process, use the local fallback for recovery, cache non-sensitive repeated query results, and show readiness state. The included rate limiter is per process; an internet-facing multi-replica service needs an edge or shared limiter.

# Retrieval

The local index stores precomputed embeddings and metadata. `HashingEmbeddingProvider` is a dependency-free deterministic demo fallback. `SentenceTransformerEmbeddingProvider` loads the configurable `intfloat/multilingual-e5-small`-style model once when selected, giving a practical multilingual semantic production path.

For every query, an embedding is generated once. Dense cosine search and the prebuilt BM25 index run concurrently. Reciprocal Rank Fusion merges rank positions rather than incomparable raw scores. The lexical reranker then scores the compact fused set using query-term coverage. Context construction removes duplicate/parent-overlapping chunks, applies a token budget, and returns source snippets.

`VectorStore` exposes `upsert`, `search`, `count`, and `health`. `LocalVectorStore` is deterministic and suitable for small/free-tier artifacts; `QdrantVectorStore` is a REST adapter for hosted Qdrant. Keep a local chunk artifact when using Qdrant because BM25 still needs document text.

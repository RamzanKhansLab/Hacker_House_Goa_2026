# Engineering decisions

- **FastAPI + Python:** typed asynchronous HTTP and an ecosystem compatible with Hugging Face, embeddings, and evaluation.
- **React/Vite rather than a component framework:** small deployable frontend with browser-native recording and no provider secrets.
- **Adapter interfaces:** local index/demo providers make tests reproducible; Qdrant/Sarvam/OpenAI-compatible adapters permit production substitution.
- **Hash embeddings in demo:** no model download or credentials needed. This is not presented as a quality baseline; switch to a small multilingual model for a real index.
- **RRF:** dense and lexical scores are not directly calibrated, while ranks are easy to merge safely.
- **Deterministic routing/grounding first:** removes unnecessary LLM calls from latency-sensitive safety and relevance decisions.
- **Separate voice/RAG timing:** remote transcription latency cannot truthfully be included in a sub-200ms RAG claim.

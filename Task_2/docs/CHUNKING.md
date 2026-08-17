# Chunking

| Strategy | Algorithm | Best use | Trade-off |
| --- | --- | --- | --- |
| Fixed | Non-overlapping token blocks | predictable storage | can split a thought |
| Sentence | Small groups of sentence boundaries | factual answers | variable chunk size |
| Sliding | overlapping token windows | exact terms across edges | duplicates candidates |
| Semantic | append sentences until a token budget | coherent explanations | heuristic boundary |
| Metadata-aware | semantic chunks plus language bucket | language-scoped search | needs complete metadata |
| Parent-child | retrieve children, retain parent relation | long-context questions | larger index |

Every chunk includes deterministic `chunk_id`, `document_id`, optional `parent_id`, language/source/target language, strategy, offsets, token count, and metadata. The query analyzer selects a strategy label deterministically (metadata-related language questions, long explanatory questions, terminology questions, or normal sentence/semantic queries). Indexing selects its materialized strategy; the router preserves this decision in telemetry for comparison rather than introducing an LLM call.

Run `python -m ingestion.chunk --strategy <name>` and measure candidate quality with the evaluation harness. Do not copy one strategy's outcome to another environment or dataset subset.

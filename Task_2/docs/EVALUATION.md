# Evaluation

`evaluation.benchmark` loads the configured index, disables query caching, repeats representative query fixtures to the requested count, and writes raw per-query latencies to CSV, a JSON summary, and a Markdown report. The default is 100 queries; use 200–500 after preparing a representative MSMARCO-XI evaluation split.

It reports Recall@1/3/5/10, hit rate, and MRR against labelled document IDs where fixtures provide them. To compare chunking, dense-only, BM25-only, hybrid, and reranker configurations, rebuild/change one configuration at a time, retain the generated results, and record model/index manifests. External STT and LLM credentials are unnecessary for the bundled demo benchmark; live provider benchmarking must state provider region and rate-limit conditions.

Guardrail cases belong in test fixtures and should include unsafe, injection, off-topic, multilingual, and low-confidence questions.

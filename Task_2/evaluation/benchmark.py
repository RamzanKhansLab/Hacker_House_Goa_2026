from __future__ import annotations

import argparse
import asyncio
import csv
import json
from pathlib import Path
from typing import Any

from app.config import Settings
from app.core.dependencies import create_services
from evaluation.latency import latency_summary
from evaluation.reports import ensure_output_dir, render_latency_report
from evaluation.retrieval_metrics import quality_metrics
from ingestion.io import read_jsonl


async def run(query_count: int, output: Path) -> None:
    samples = read_jsonl(Path("data/demo/queries.jsonl"))
    if not samples:
        raise RuntimeError("No evaluation queries found")
    services = create_services(Settings(query_cache_size=0))
    rows: list[dict[str, Any]] = []
    rankings: list[tuple[str, list[str]]] = []
    try:
        for index in range(query_count):
            sample = samples[index % len(samples)]
            response = await services.orchestrator.answer(sample["query"], sample.get("language"))
            flattened = response.latency.model_dump()
            rows.append({"query": sample["query"], "guardrail_status": response.guardrail_status, **flattened})
            rankings.append((str(sample["relevant_document_id"]), [source.document_id for source in response.sources]))
    finally:
        await services.close()
    ensure_output_dir(output)
    fieldnames = list(rows[0].keys())
    with (output / "latency_results.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    latency_keys = [key for key in rows[0] if key.endswith("_ms")]
    summary = {key: latency_summary(rows, key) for key in latency_keys}
    quality = quality_metrics(rankings)
    (output / "latency_results.json").write_text(json.dumps({"summary": summary, "quality": quality, "rows": rows}, indent=2), encoding="utf-8")
    (output / "LATENCY_REPORT.md").write_text(render_latency_report(summary, quality, len(rows)), encoding="utf-8")
    print(f"Wrote measured results for {len(rows)} queries to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark warm local RAG latency and retrieval quality.")
    parser.add_argument("--queries", type=int, default=100, help="Use at least 100 for submission reporting.")
    parser.add_argument("--output", type=Path, default=Path("evaluation_results"))
    args = parser.parse_args()
    if args.queries < 1:
        raise SystemExit("--queries must be positive")
    asyncio.run(run(args.queries, args.output))


if __name__ == "__main__":
    main()

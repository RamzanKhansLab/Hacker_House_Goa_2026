from __future__ import annotations

import argparse
import hashlib
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from ingestion.io import read_jsonl, write_jsonl

_SPACE = re.compile(r"\s+", re.UNICODE)


def clean_text(value: object) -> str:
    return _SPACE.sub(" ", str(value or "")).strip()


def flatten_text(value: object) -> list[str]:
    if isinstance(value, str):
        return [clean_text(value)] if clean_text(value) else []
    if isinstance(value, list):
        return [text for item in value for text in flatten_text(item)]
    if isinstance(value, dict):
        preferred = value.get("text") or value.get("passage_text") or value.get("passages")
        return flatten_text(preferred) if preferred is not None else []
    return []


def _first(row: dict[str, Any], names: tuple[str, ...], fallback: str = "") -> str:
    for name in names:
        if name in row and row[name] is not None:
            text = clean_text(row[name])
            if text:
                return text
    return fallback


def normalize_record(row: dict[str, Any], fallback_language: str = "unknown") -> list[dict[str, Any]]:
    """Normalize divergent HF schemas while retaining source/target language metadata."""
    query = _first(row, ("query", "question", "query_text"))
    answer = _first(row, ("answer", "answers", "wellFormedAnswers"))
    language = _first(row, ("language", "lang", "target_language", "target_lang"), fallback_language).split("-")[0]
    source_language = _first(row, ("source_language", "source_lang", "src_lang")) or None
    target_language = _first(row, ("target_language", "target_lang", "tgt_lang")) or None
    passages_value = row.get("passages") or row.get("passage") or row.get("documents") or row.get("context")
    passages = flatten_text(passages_value)
    if not passages:
        passages = [answer] if answer else []
    normalized: list[dict[str, Any]] = []
    source_id = clean_text(row.get("id") or row.get("query_id") or query)
    for passage_number, passage in enumerate(passages):
        passage = clean_text(passage)
        if len(passage) < 8:
            continue
        stable_id = hashlib.sha256(f"{source_id}|{passage_number}|{passage}".encode("utf-8")).hexdigest()[:24]
        normalized.append(
            {
                "id": f"msmarco-xi:{stable_id}",
                "text": passage,
                "title": query or None,
                "language": language,
                "source_language": source_language,
                "target_language": target_language,
                "metadata": {"source_id": source_id, "query": query, "answer": answer, "passage_number": passage_number},
            }
        )
    return normalized


def normalize_rows(rows: Iterable[dict[str, Any]], fallback_language: str = "unknown") -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for row in rows:
        for record in normalize_record(row, fallback_language):
            unique[record["id"]] = record
    return list(unique.values())


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize MSMARCO-XI rows into retrieval documents.")
    parser.add_argument("--input", type=Path, default=Path("data/raw/msmarco_xi.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/records.jsonl"))
    parser.add_argument("--language", default="unknown", help="Used only when source rows lack a language field.")
    args = parser.parse_args()
    records = normalize_rows(read_jsonl(args.input), args.language)
    print(f"Normalized {write_jsonl(args.output, records)} documents to {args.output}")


if __name__ == "__main__":
    main()

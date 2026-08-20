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
        # MSMARCO-XI stores parallel passage lists under these names. Prefer
        # the translated passage for a translated configuration, then retain
        # generic schema compatibility for other supported inputs.
        for key in ("Translated_passages", "translated_passages", "English_passages", "passages", "text", "passage_text"):
            if value.get(key) is not None:
                return flatten_text(value[key])
        return []
    return []


def _first(row: dict[str, Any], names: tuple[str, ...], fallback: str = "") -> str:
    for name in names:
        if name in row and row[name] is not None:
            text = clean_text(row[name])
            if text:
                return text
    return fallback


def _passages_for_index(value: object, max_selected: int | None = None) -> list[str]:
    """Extract MSMARCO-XI passages, prioritising labelled relevant evidence.

    Each MS MARCO record contains roughly ten candidate passages. Indexing all
    candidates inflates a 5k-record experiment into about 50k chunks and adds
    known-negative passages. When `is_selected` labels are present, retaining
    selected translated passages gives a compact, higher-quality corpus.
    """
    if not isinstance(value, dict):
        return flatten_text(value)
    texts = value.get("Translated_passages") or value.get("translated_passages")
    selected = value.get("is_selected")
    if isinstance(texts, list) and isinstance(selected, list) and len(texts) == len(selected):
        chosen = [text for text, flag in zip(texts, selected, strict=True) if flag]
        if max_selected:
            chosen = chosen[:max_selected]
        if chosen:
            return flatten_text(chosen)
        # A labelled MSMARCO-XI row with no selected candidate must not add
        # all known-negative candidates to a compact retrieval experiment.
        # The caller will use the translated answer when available.
        return []
    return flatten_text(value)


def normalize_record(
    row: dict[str, Any], fallback_language: str = "unknown", max_selected_passages: int | None = None
) -> list[dict[str, Any]]:
    """Normalize divergent HF schemas while retaining source/target language metadata."""
    query = _first(row, ("query", "question", "query_text"))
    answer = _first(row, ("answer", "Answer", "answers", "wellFormedAnswers"))
    target_language = _first(row, ("target_language", "target_lang", "tgt_lang")) or None
    language = _language_code(
        _first(row, ("language", "lang")) or target_language or fallback_language
    )
    source_language = _first(row, ("source_language", "source_lang", "src_lang")) or None
    passages_value = row.get("passages") or row.get("passage") or row.get("documents") or row.get("context")
    passages = _passages_for_index(passages_value, max_selected_passages)
    if not passages:
        passages = [answer] if answer else []
    normalized: list[dict[str, Any]] = []
    source_id = clean_text(row.get("id") or row.get("query_id") or query)
    for passage_number, passage in enumerate(passages):
        passage = clean_text(passage)
        if len(passage) < 8:
            continue
        # MSMARCO-XI parallel language shards reuse query ids.  Namespace the
        # source identifier so translations cannot collide in a multilingual
        # index or be merged accidentally during fusion.
        stable_id = hashlib.sha256(f"{language}|{source_id}|{passage_number}|{passage}".encode("utf-8")).hexdigest()[:24]
        normalized.append(
            {
                "id": f"msmarco-xi:{language}:{stable_id}",
                "text": passage,
                "title": query or None,
                "language": language,
                "source_language": source_language,
                "target_language": target_language,
                "metadata": {"source_id": source_id, "query": query, "answer": answer, "passage_number": passage_number},
            }
        )
    return normalized


def _language_code(value: str) -> str:
    """Convert BCP-47 and IndicTrans2 codes to the retrieval language code."""
    prefixes = {
        "asm": "as", "ben": "bn", "guj": "gu", "hin": "hi", "kan": "kn", "mal": "ml",
        "mar": "mr", "nep": "ne", "ory": "or", "pan": "pa", "san": "sa", "tam": "ta",
        "tel": "te", "urd": "ur", "eng": "en",
    }
    base = clean_text(value).split("-", 1)[0].split("_", 1)[0].lower()
    return prefixes.get(base, base or "unknown")


def normalize_rows(
    rows: Iterable[dict[str, Any],], fallback_language: str = "unknown", max_selected_passages: int | None = None
) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for row in rows:
        for record in normalize_record(row, fallback_language, max_selected_passages):
            unique[record["id"]] = record
    return list(unique.values())


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize MSMARCO-XI rows into retrieval documents.")
    parser.add_argument("--input", type=Path, default=Path("data/raw/msmarco_xi.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/records.jsonl"))
    parser.add_argument("--language", default="unknown", help="Used only when source rows lack a language field.")
    parser.add_argument(
        "--max-selected-passages", type=int, default=1,
        help="Keep at most this many labelled relevant MSMARCO-XI passages per query; use 0 for all selected passages.",
    )
    args = parser.parse_args()
    if args.max_selected_passages < 0:
        raise SystemExit("--max-selected-passages must be non-negative.")
    records = normalize_rows(
        read_jsonl(args.input), args.language, args.max_selected_passages or None
    )
    print(f"Normalized {write_jsonl(args.output, records)} documents to {args.output}")


if __name__ == "__main__":
    main()

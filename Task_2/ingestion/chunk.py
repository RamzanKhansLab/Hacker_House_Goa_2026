from __future__ import annotations

import argparse
from pathlib import Path

from app.services.chunking import chunk_records
from ingestion.io import read_jsonl, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply a deterministic chunking strategy to normalized documents.")
    parser.add_argument("--input", type=Path, default=Path("data/processed/records.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/chunks.jsonl"))
    parser.add_argument("--strategy", choices=["fixed", "sentence", "sliding", "semantic", "metadata", "parent_child"], default="semantic")
    args = parser.parse_args()
    chunks = chunk_records(read_jsonl(args.input), args.strategy)
    print(f"Created {write_jsonl(args.output, (chunk.as_dict() for chunk in chunks))} chunks using {args.strategy}")


if __name__ == "__main__":
    main()

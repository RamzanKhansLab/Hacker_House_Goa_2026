from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.config import Settings
from app.core.dependencies import _create_embedder
from app.services.types import Chunk
from ingestion.io import read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate precomputed embeddings for a chunk JSONL artifact.")
    parser.add_argument("--input", type=Path, default=Path("data/processed/chunks.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/embeddings.json"))
    parser.add_argument("--backend", choices=["hash", "sentence_transformer"])
    parser.add_argument("--model")
    args = parser.parse_args()
    settings = Settings(embedding_backend=args.backend or Settings().embedding_backend, embedding_model=args.model or Settings().embedding_model)
    chunks = [Chunk.from_dict(row) for row in read_jsonl(args.input)]
    vectors = _create_embedder(settings).embed([chunk.text for chunk in chunks])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"dimension": len(vectors[0]) if vectors else 0, "vectors": vectors}), encoding="utf-8")
    print(f"Embedded {len(vectors)} chunks to {args.output}")


if __name__ == "__main__":
    main()

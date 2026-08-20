from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from app.config import Settings
from app.core.dependencies import _create_embedder
from app.services.chunking import chunk_records
from app.services.retrieval.local import LocalVectorStore
from ingestion.io import read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a persistent local vector index; never run during API startup.")
    parser.add_argument("--input", type=Path, default=Path("data/processed/records.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("data/index/index.json"))
    parser.add_argument("--strategy", choices=["fixed", "sentence", "sliding", "semantic", "metadata", "parent_child"], default="semantic")
    parser.add_argument("--backend", choices=["hash", "sentence_transformer"])
    parser.add_argument("--model")
    parser.add_argument("--demo", action="store_true", help="Build from bundled demo documents rather than downloaded data.")
    args = parser.parse_args()
    source = Path("data/demo/documents.jsonl") if args.demo else args.input
    if not source.exists():
        raise SystemExit("Input does not exist. Run download_dataset and normalize first, or pass --demo.")
    base = Settings()
    settings = Settings(embedding_backend=args.backend or base.embedding_backend, embedding_model=args.model or base.embedding_model)
    records = read_jsonl(source)
    chunks = chunk_records(records, args.strategy)
    vectors = _create_embedder(settings).embed_documents([chunk.text for chunk in chunks])
    index = LocalVectorStore()
    index.upsert(chunks, vectors)
    manifest: dict[str, object] = {
        "dataset": "ai4bharat/MSMARCO-XI" if not args.demo else "bundled demo subset",
        "embedding_model": settings.embedding_model,
        "embedding_backend": settings.embedding_backend,
        "chunking_strategy": args.strategy,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "document_count": len(records),
        "chunk_count": len(chunks),
        "languages": sorted({str(record.get("language", "unknown")) for record in records}),
        "index_version": "1",
    }
    index.save(args.output, manifest)
    print(f"Indexed {len(chunks)} chunks at {args.output}")


if __name__ == "__main__":
    main()

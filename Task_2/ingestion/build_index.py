from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.config import Settings
from app.core.dependencies import _create_embedder
from app.services.chunking import chunk_records
from app.services.retrieval.local import LocalVectorStore
from app.services.retrieval.qdrant import QdrantVectorStore
from ingestion.io import read_jsonl


def ensure_qdrant_collection(
    url: str,
    api_key: str | None,
    collection: str,
    vector_size: int,
    timeout: float,
) -> None:
    headers = {"api-key": api_key} if api_key else {}

    response = httpx.get(
        f"{url.rstrip('/')}/collections/{collection}",
        headers=headers,
        timeout=timeout,
    )

    if response.status_code == 200:
        print(f"Qdrant collection '{collection}' already exists.")
        return

    if response.status_code != 404:
        response.raise_for_status()

    print(
        f"Creating Qdrant collection '{collection}' "
        f"with vector size {vector_size}..."
    )

    response = httpx.put(
        f"{url.rstrip('/')}/collections/{collection}",
        headers=headers,
        json={
            "vectors": {
                "size": vector_size,
                "distance": "Cosine",
            }
        },
        timeout=timeout,
    )
    response.raise_for_status()

    print(f"Created Qdrant collection '{collection}'.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a persistent vector index; never run during API startup."
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/records.jsonl"),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/index/index.json"),
    )

    parser.add_argument(
        "--strategy",
        choices=[
            "fixed",
            "sentence",
            "sliding",
            "semantic",
            "metadata",
            "parent_child",
        ],
        default="semantic",
    )

    parser.add_argument(
        "--backend",
        choices=["hash", "sentence_transformer"],
    )

    parser.add_argument("--model")

    parser.add_argument(
        "--vector-store",
        choices=["local", "qdrant"],
        default=None,
        help="Override VECTOR_STORE configuration.",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=256,
        help="Number of vectors per Qdrant upload request.",
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Build from bundled demo documents rather than downloaded data.",
    )

    args = parser.parse_args()

    source = (
        Path("data/demo/documents.jsonl")
        if args.demo
        else args.input
    )

    if not source.exists():
        raise SystemExit(
            "Input does not exist. Run download_dataset and normalize first, "
            "or pass --demo."
        )

    base = Settings()

    settings = Settings(
        embedding_backend=args.backend or base.embedding_backend,
        embedding_model=args.model or base.embedding_model,
    )

    vector_store = args.vector_store or base.vector_store

    records = read_jsonl(source)

    print(f"Loaded {len(records)} records.")

    chunks = chunk_records(records, args.strategy)

    print(f"Generated {len(chunks)} chunks.")

    embedder = _create_embedder(settings)

    print(
        f"Generating embeddings using "
        f"{settings.embedding_backend} / {settings.embedding_model}..."
    )

    vectors = embedder.embed_documents(
        [chunk.text for chunk in chunks]
    )

    if not vectors:
        raise SystemExit("Embedding generation returned no vectors.")

    vector_size = len(vectors[0])

    print(
        f"Generated {len(vectors)} vectors "
        f"with dimension {vector_size}."
    )

    manifest: dict[str, object] = {
        "dataset": (
            "ai4bharat/MSMARCO-XI"
            if not args.demo
            else "bundled demo subset"
        ),
        "embedding_model": settings.embedding_model,
        "embedding_backend": settings.embedding_backend,
        "chunking_strategy": args.strategy,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "document_count": len(records),
        "chunk_count": len(chunks),
        "languages": sorted(
            {
                str(record.get("language", "unknown"))
                for record in records
            }
        ),
        "index_version": "1",
        "vector_store": vector_store,
        "vector_size": vector_size,
    }

    if vector_store == "local":
        index = LocalVectorStore()

        index.upsert(chunks, vectors)

        index.save(args.output, manifest)

        print(
            f"Indexed {len(chunks)} chunks "
            f"at {args.output}"
        )

    elif vector_store == "qdrant":
        if not base.qdrant_url:
            raise SystemExit(
                "QDRANT_URL is required when VECTOR_STORE=qdrant."
            )

        ensure_qdrant_collection(
            url=base.qdrant_url,
            api_key=base.qdrant_api_key,
            collection=base.qdrant_collection,
            vector_size=vector_size,
            timeout=base.vector_db_timeout_seconds,
        )

        store = QdrantVectorStore(
            base.qdrant_url,
            base.qdrant_api_key,
            base.qdrant_collection,
            base.vector_db_timeout_seconds,
        )

        total = len(chunks)

        for start in range(0, total, args.batch_size):
            end = min(start + args.batch_size, total)

            store.upsert(
                chunks[start:end],
                vectors[start:end],
            )

            print(
                f"Uploaded {end}/{total} chunks "
                f"to Qdrant..."
            )

        count = store.count()

        print(
            f"Finished indexing {total} chunks into "
            f"Qdrant collection '{base.qdrant_collection}'."
        )

        print(f"Qdrant collection count: {count}")

    else:
        raise SystemExit(
            f"Unsupported vector store: {vector_store}"
        )


if __name__ == "__main__":
    main()
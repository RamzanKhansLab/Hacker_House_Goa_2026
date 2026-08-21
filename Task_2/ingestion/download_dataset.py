from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from pathlib import Path

from ingestion.io import write_jsonl

DATASET_ID = "ai4bharat/MSMARCO-XI"
_LANGUAGE_FILES = {
    "as": "asm", "bn": "ben", "gu": "guj", "hi": "hin", "kn": "kan", "ml": "mal", "mr": "mar",
    "ne": "nep", "or": "ori", "pa": "pan", "sa": "san", "ta": "tam", "te": "tel", "ur": "urd",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a bounded MSMARCO-XI language split for offline indexing.")
    parser.add_argument("--config", default="hi", choices=sorted(_LANGUAGE_FILES), help="MSMARCO-XI language configuration.")
    parser.add_argument("--split", default="validation", choices=["train", "validation"])
    parser.add_argument("--limit", type=int, default=5000, help="Maximum records to persist; use 0 for all records.")
    parser.add_argument("--output", type=Path, default=Path("data/raw/msmarco_xi.jsonl"))
    parser.add_argument(
        "--max-source-mb", type=int, default=1024,
        help="Refuse a source Parquet file larger than this unless you explicitly raise the limit.",
    )
    args = parser.parse_args()
    if args.limit < 0 or args.max_source_mb < 1:
        raise SystemExit("--limit must be non-negative and --max-source-mb must be positive.")
    try:
        from huggingface_hub import hf_hub_download, repo_info  # type: ignore[import-not-found]
        from pyarrow.parquet import ParquetFile  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SystemExit("Install optional ML dependencies first: python -m pip install -e '.[ml]'") from exc

    split_suffix = "train" if args.split == "train" else "val"
    filename = f"{args.split}/{_LANGUAGE_FILES[args.config]}{split_suffix}.parquet"
    info = repo_info(DATASET_ID, repo_type="dataset", files_metadata=True)
    size = next((item.size for item in info.siblings if item.rfilename == filename), None)
    if size is None:
        raise SystemExit(f"Could not locate {filename} in {DATASET_ID}.")
    if size > args.max_source_mb * 1024 * 1024:
        raise SystemExit(
            f"{filename} is {size / 1024 / 1024:.1f} MB; exceeds --max-source-mb={args.max_source_mb}. "
            "Choose validation or explicitly raise the limit after checking disk space."
        )
    local_path = hf_hub_download(DATASET_ID, filename=filename, repo_type="dataset")
    parquet = ParquetFile(local_path)

    def rows() -> Iterator[dict[str, object]]:
        written = 0
        for batch in parquet.iter_batches(batch_size=512):
            for row in batch.to_pylist():
                yield row
                written += 1
                if args.limit and written >= args.limit:
                    return

    count = write_jsonl(args.output, rows())
    manifest_path = args.output.with_suffix(".manifest.json")
    manifest_path.write_text(
        json.dumps(
            {
                "dataset": DATASET_ID,
                "config": args.config,
                "split": args.split,
                "source_file": filename,
                "source_size_bytes": size,
                "record_count": count,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"output": str(args.output), "records": count, "config": args.config, "split": args.split}))


if __name__ == "__main__":
    main()

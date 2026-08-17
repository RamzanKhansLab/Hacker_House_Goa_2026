from __future__ import annotations

import argparse
import json
from pathlib import Path

from ingestion.io import write_jsonl

DATASET_ID = "ai4bharat/MSMARCO-XI"


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a bounded MSMARCO-XI split for offline indexing.")
    parser.add_argument("--config", help="Hugging Face configuration name. Omit to choose the first available config.")
    parser.add_argument("--split", default="train")
    parser.add_argument("--limit", type=int, default=5000, help="Maximum records to persist; use 0 for all records.")
    parser.add_argument("--output", type=Path, default=Path("data/raw/msmarco_xi.jsonl"))
    args = parser.parse_args()
    try:
        from datasets import (  # type: ignore[import-not-found]
            get_dataset_config_names,
            load_dataset,
        )
    except ImportError as exc:
        raise SystemExit("Install optional ML dependencies first: python -m pip install -e '.[ml]'") from exc
    config = args.config or get_dataset_config_names(DATASET_ID)[0]
    dataset = load_dataset(DATASET_ID, config, split=args.split)
    rows = (dict(row) for index, row in enumerate(dataset) if not args.limit or index < args.limit)
    count = write_jsonl(args.output, rows)
    manifest_path = args.output.with_suffix(".manifest.json")
    manifest_path.write_text(
        json.dumps({"dataset": DATASET_ID, "config": config, "split": args.split, "record_count": count}, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({"output": str(args.output), "records": count, "config": config}))


if __name__ == "__main__":
    main()

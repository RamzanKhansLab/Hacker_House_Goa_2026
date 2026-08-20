from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ingestion.io import read_jsonl


def main() -> None:
    # Preserve Indic samples when this command is run from Windows PowerShell.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Inspect an acquired MSMARCO-XI JSONL file without modifying it.")
    parser.add_argument("--input", type=Path, default=Path("data/raw/msmarco_xi.jsonl"))
    args = parser.parse_args()
    rows = read_jsonl(args.input)
    if not rows:
        raise SystemExit("No records found.")
    field_types: dict[str, set[str]] = {}
    for row in rows[:100]:
        for key, value in row.items():
            field_types.setdefault(key, set()).add(type(value).__name__)
    print(json.dumps({"records": len(rows), "fields": {key: sorted(types) for key, types in field_types.items()}, "sample": rows[0]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

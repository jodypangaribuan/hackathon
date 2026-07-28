"""Lightweight, deterministic source-file inventory for A2/A3 handoff."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .manifest import sha256_file


def _csv_profile(path: Path, encoding: str) -> dict[str, Any]:
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
        row_count = sum(1 for _ in reader)
    return {
        "columns": header,
        "column_count": len(header),
        "row_count_excluding_header": row_count,
    }


def inventory_dataset(dataset_dir: Path, encoding: str = "utf-8-sig") -> dict[str, Any]:
    """Inventory source files without modifying or loading them fully into memory."""

    dataset_dir = dataset_dir.resolve()
    if not dataset_dir.is_dir():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    files: list[dict[str, Any]] = []
    for path in sorted(item for item in dataset_dir.iterdir() if item.is_file()):
        record: dict[str, Any] = {
            "filename": path.name,
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "suffix": path.suffix.lower(),
        }
        if path.suffix.lower() == ".csv":
            try:
                record.update(_csv_profile(path, encoding))
                record["encoding"] = encoding
                record["read_error"] = None
            except (UnicodeDecodeError, csv.Error, OSError) as error:
                record["read_error"] = f"{type(error).__name__}: {error}"
        files.append(record)

    return {
        "dataset_dir": str(dataset_dir),
        "file_count": len(files),
        "files": files,
    }


def write_inventory(inventory: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    """Write machine-readable JSON and review-friendly CSV inventory files."""

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "data_inventory.json"
    csv_path = output_dir / "data_inventory.csv"
    json_path.write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    fields = (
        "filename",
        "suffix",
        "size_bytes",
        "sha256",
        "encoding",
        "row_count_excluding_header",
        "column_count",
        "read_error",
    )
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(inventory["files"])
    return json_path, csv_path

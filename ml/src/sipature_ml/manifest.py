"""Artifact manifest helpers for provenance and reproducibility."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the SHA-256 digest for a file without loading it fully into memory."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(
    *,
    artifact_version: str,
    pipeline_version: str,
    config: dict[str, Any],
    source_files: list[Path],
) -> dict[str, Any]:
    """Build a JSON-serializable artifact provenance manifest."""

    return {
        "artifact_version": artifact_version,
        "pipeline_version": pipeline_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config": config,
        "sources": [
            {"path": str(path), "sha256": sha256_file(path)} for path in source_files
        ],
    }


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    """Write a manifest deterministically for readable diffs and stable hashing."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

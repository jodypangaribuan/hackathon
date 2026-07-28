"""Environment and configuration capture for reproducible runs."""

from __future__ import annotations

import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .manifest import sha256_file
from .paths import PATHS

TRACKED_PACKAGES = (
    "numpy",
    "pandas",
    "pyarrow",
    "scikit-learn",
    "PyYAML",
    "rapidfuzz",
    "torch",
    "transformers",
    "datasets",
    "accelerate",
    "evaluate",
)


def _git_value(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ("git", *args),
            cwd=PATHS.root.parent,
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def package_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for package in TRACKED_PACKAGES:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "not-installed"
    return versions


def build_environment_snapshot() -> dict[str, Any]:
    configs = sorted((PATHS.root / "configs").glob("*.yaml"))
    return {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "git_commit": _git_value("rev-parse", "HEAD"),
        "git_dirty": bool(_git_value("status", "--porcelain")),
        "seed_environment": os.environ.get("PYTHONHASHSEED", "not-set"),
        "packages": package_versions(),
        "configs": {path.name: sha256_file(path) for path in configs},
    }


def write_environment_snapshot(output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build_environment_snapshot(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output

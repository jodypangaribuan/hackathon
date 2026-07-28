"""Google Drive workspace bootstrap shared by SIPATURE Colab notebooks."""

from __future__ import annotations

from pathlib import Path

DRIVE_DIRECTORIES = (
    "data/raw",
    "data/interim",
    "data/processed",
    "data/annotations",
    "data/splits",
    "models",
    "predictions",
    "metrics",
    "figures",
    "reports",
    "runs",
)


def bootstrap_drive(project_root: Path) -> tuple[Path, ...]:
    """Create the persistent Drive layout and return all created paths."""

    paths = tuple(project_root / relative for relative in DRIVE_DIRECTORIES)
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
    return paths

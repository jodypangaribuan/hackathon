"""Configuration loading with explicit project-relative paths."""

from pathlib import Path
from typing import Any

import yaml


ML_ROOT = Path(__file__).resolve().parents[2]


def load_config(name: str) -> dict[str, Any]:
    """Load a YAML config from ``ml/configs``.

    ``name`` may be supplied with or without the ``.yaml`` suffix.
    """

    filename = name if name.endswith(".yaml") else f"{name}.yaml"
    path = ML_ROOT / "configs" / filename
    if not path.is_file():
        raise FileNotFoundError(f"Configuration not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Configuration must contain a mapping: {path}")
    return value

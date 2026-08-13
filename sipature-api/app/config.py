"""Application configuration, resolved from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "SIPATURE Inference"
    app_version: str = "1.0.0"
    model_dir: Path = Path("/app/model")
    max_chars: int = 5000

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            model_dir=Path(os.environ.get("MODEL_DIR", "/app/model")),
            max_chars=int(os.environ.get("MAX_CHARS", "5000")),
        )


settings = Settings.from_env()

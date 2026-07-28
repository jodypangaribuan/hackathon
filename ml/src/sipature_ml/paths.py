"""Canonical filesystem paths for all pipeline stages."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    data: Path
    raw: Path
    interim: Path
    processed: Path
    annotations: Path
    splits: Path
    artifacts: Path

    @classmethod
    def from_root(cls, root: Path) -> "ProjectPaths":
        root = root.resolve()
        data = root / "data"
        return cls(
            root=root,
            data=data,
            raw=data / "raw",
            interim=data / "interim",
            processed=data / "processed",
            annotations=data / "annotations",
            splits=data / "splits",
            artifacts=root / "artifacts",
        )

    def ensure_generated_directories(self) -> None:
        for path in (
            self.raw,
            self.interim,
            self.processed,
            self.annotations,
            self.splits,
            self.artifacts,
        ):
            path.mkdir(parents=True, exist_ok=True)


PATHS = ProjectPaths.from_root(Path(__file__).resolve().parents[2])

"""Command-line entry point for pipeline discovery and stage execution."""

import argparse
import json
from pathlib import Path

from .colab import bootstrap_drive
from .config import load_config
from .environment import build_environment_snapshot, write_environment_snapshot
from .inventory import inventory_dataset, write_inventory
from .paths import PATHS
from .stages import PIPELINE_ORDER, Stage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sipature-ml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("stages", help="List pipeline stages in execution order")
    subparsers.add_parser("validate-config", help="Load and print core configuration")
    subparsers.add_parser("doctor", help="Print environment and reproducibility metadata")

    snapshot = subparsers.add_parser("snapshot-run", help="Write run environment metadata")
    snapshot.add_argument("--output", type=Path, required=True)

    drive = subparsers.add_parser("bootstrap-drive", help="Create persistent Colab Drive layout")
    drive.add_argument("--root", type=Path, required=True)

    run = subparsers.add_parser("run", help="Run one pipeline stage")
    run.add_argument("stage", choices=[stage.value for stage in Stage])
    run.add_argument("--dataset-dir", type=Path)
    run.add_argument("--output-dir", type=Path, default=PATHS.artifacts / "reports")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "stages":
        for index, stage in enumerate(PIPELINE_ORDER, start=1):
            print(f"{index:02d}. {stage.value}")
        return 0
    if args.command == "validate-config":
        PATHS.ensure_generated_directories()
        print(json.dumps(load_config("pipeline"), indent=2))
        return 0
    if args.command == "doctor":
        print(json.dumps(build_environment_snapshot(), indent=2, sort_keys=True))
        return 0
    if args.command == "snapshot-run":
        output = write_environment_snapshot(args.output)
        print(output)
        return 0
    if args.command == "bootstrap-drive":
        for path in bootstrap_drive(args.root):
            print(path)
        return 0
    if args.command == "run" and args.stage == Stage.INVENTORY.value:
        if args.dataset_dir is None:
            raise SystemExit("--dataset-dir is required for the inventory stage")
        config = load_config("pipeline")
        inventory = inventory_dataset(
            args.dataset_dir,
            encoding=config["data"]["source_encoding"],
        )
        for output in write_inventory(inventory, args.output_dir):
            print(output)
        return 0
    raise NotImplementedError(
        f"Stage '{args.stage}' is declared but not implemented. "
        "Implement and test the stage before marking its TODO complete."
    )


if __name__ == "__main__":
    raise SystemExit(main())

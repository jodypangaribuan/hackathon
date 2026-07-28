"""Command-line entry point for pipeline discovery and stage execution."""

import argparse
import json

from .config import load_config
from .paths import PATHS
from .stages import PIPELINE_ORDER, Stage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sipature-ml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("stages", help="List pipeline stages in execution order")
    subparsers.add_parser("validate-config", help="Load and print core configuration")

    run = subparsers.add_parser("run", help="Run one pipeline stage")
    run.add_argument("stage", choices=[stage.value for stage in Stage])
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
    raise NotImplementedError(
        f"Stage '{args.stage}' is declared but not implemented. "
        "Implement and test the stage before marking its TODO complete."
    )


if __name__ == "__main__":
    raise SystemExit(main())

"""Command-line entry point for pipeline discovery and stage execution."""

import argparse
import json
from pathlib import Path

from .a9 import run_aggregation, run_export, run_inference, run_prioritization
from .annotation import (
    evaluate_agreement,
    freeze_gold,
    run_annotation_sampling,
    run_silver_annotation,
    validate_annotation_files,
    validate_silver_records,
)
from .baselines import run_baselines
from .cleaning import run_cleaning
from .colab import bootstrap_drive
from .comparison import run_preliminary_final_comparison
from .config import load_config
from .eda import run_eda
from .entity_resolution import run_entity_resolution
from .environment import build_environment_snapshot, write_environment_snapshot
from .evaluation import run_calibration, run_locked_test_evaluation
from .gold_baselines import run_gold_baselines
from .indobert import run_indobert_training
from .indobert_gold import run_gold_indobert_evaluation
from .inventory import inventory_dataset, write_inventory
from .paths import PATHS
from .quality_figures import (
    generate_annotation_figures,
    generate_quality_figures,
    generate_silver_figures,
)
from .split import run_split
from .stages import PIPELINE_ORDER, Stage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sipature-ml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("stages", help="List pipeline stages in execution order")
    subparsers.add_parser("validate-config", help="Load and print core configuration")
    subparsers.add_parser("doctor", help="Print environment and reproducibility metadata")

    quality = subparsers.add_parser("quality-figures", help="Generate cleaning/entity report figures")
    quality.add_argument("--report-dir", type=Path, default=PATHS.artifacts / "reports")
    quality.add_argument("--processed-dir", type=Path, default=PATHS.processed)
    quality.add_argument("--figure-dir", type=Path, required=True)

    annotation_figures = subparsers.add_parser(
        "annotation-figures", help="Generate aggregate annotation sampling figures"
    )
    annotation_figures.add_argument("--annotation-dir", type=Path, default=PATHS.annotations)
    annotation_figures.add_argument("--report-dir", type=Path, default=PATHS.artifacts / "reports")
    annotation_figures.add_argument("--figure-dir", type=Path, required=True)

    annotation_sample = subparsers.add_parser(
        "annotation-sample", help="Generate pilot/main annotation samples and assignments"
    )
    annotation_sample.add_argument("--processed-dir", type=Path, default=PATHS.processed)
    annotation_sample.add_argument("--annotation-dir", type=Path, default=PATHS.annotations)
    annotation_sample.add_argument("--report-dir", type=Path, default=PATHS.artifacts / "reports")

    annotation_validate = subparsers.add_parser(
        "annotation-validate", help="Validate annotation JSONL files"
    )
    annotation_validate.add_argument("paths", nargs="+", type=Path)
    annotation_validate.add_argument("--require-completed", action="store_true")

    agreement = subparsers.add_parser("annotation-agreement", help="Calculate pilot agreement")
    agreement.add_argument("paths", nargs="+", type=Path)
    agreement.add_argument("--output", type=Path, required=True)

    gold = subparsers.add_parser("freeze-gold", help="Freeze gold data after all gates pass")
    gold.add_argument("paths", nargs="+", type=Path)
    gold.add_argument("--adjudicated", type=Path, required=True)
    gold.add_argument("--metrics", type=Path, required=True)
    gold.add_argument("--output", type=Path, required=True)

    silver = subparsers.add_parser(
        "silver-annotate", help="Generate AI-assisted silver labels and consistency audit"
    )
    silver.add_argument("--processed-dir", type=Path, default=PATHS.processed)
    silver.add_argument("--annotation-dir", type=Path, default=PATHS.annotations)
    silver.add_argument("--report-dir", type=Path, default=PATHS.artifacts / "reports")

    silver_validate = subparsers.add_parser(
        "silver-validate", help="Validate AI-assisted silver annotation JSONL"
    )
    silver_validate.add_argument("path", type=Path)

    silver_figures = subparsers.add_parser(
        "silver-figures", help="Generate aggregate AI-assisted silver label figures"
    )
    silver_figures.add_argument("--annotation-dir", type=Path, default=PATHS.annotations)
    silver_figures.add_argument("--figure-dir", type=Path, required=True)

    split = subparsers.add_parser("split-silver", help="Create locked leakage-safe silver splits")
    split.add_argument("--processed-dir", type=Path, default=PATHS.processed)
    split.add_argument("--annotation-dir", type=Path, default=PATHS.annotations)
    split.add_argument("--split-dir", type=Path, default=PATHS.splits)
    split.add_argument("--report-dir", type=Path, default=PATHS.artifacts / "reports")

    baselines = subparsers.add_parser(
        "train-baselines", help="Train and evaluate keyword/TF-IDF silver baselines"
    )
    baselines.add_argument("--split-dir", type=Path, default=PATHS.splits)
    baselines.add_argument("--artifact-dir", type=Path, default=PATHS.artifacts)
    baselines.add_argument("--figure-dir", type=Path, required=True)

    gold_baselines = subparsers.add_parser(
        "evaluate-gold-baselines", help="Evaluate keyword/TF-IDF baselines against human-gold labels"
    )
    gold_baselines.add_argument("--split-dir", type=Path, default=PATHS.splits)
    gold_baselines.add_argument("--gold", type=Path, default=PATHS.annotations / "gold" / "gold.jsonl")
    gold_baselines.add_argument("--artifact-dir", type=Path, default=PATHS.artifacts)

    compare = subparsers.add_parser(
        "compare-preliminary-final", help="Compare preliminary (silver) vs final (gold) model scores"
    )
    compare.add_argument("--metrics-dir", type=Path, default=PATHS.artifacts / "metrics")
    compare.add_argument("--figure-dir", type=Path, default=PATHS.artifacts / "figures" / "comparison")

    gold_indobert = subparsers.add_parser(
        "evaluate-gold-indobert", help="Evaluate the frozen A7 IndoBERT against human-gold labels (GPU)"
    )
    gold_indobert.add_argument("--split-dir", type=Path, default=PATHS.splits)
    gold_indobert.add_argument("--model-run-dir", type=Path, required=True)
    gold_indobert.add_argument("--calibration-dir", type=Path, required=True)
    gold_indobert.add_argument("--gold", type=Path, default=PATHS.annotations / "gold" / "gold.jsonl")
    gold_indobert.add_argument("--output-dir", type=Path, required=True)

    indobert = subparsers.add_parser(
        "train-indobert", help="Train IndoBERT tasks on train/validation only (GPU)"
    )
    indobert.add_argument("--split-dir", type=Path, default=PATHS.splits)
    indobert.add_argument("--artifact-dir", type=Path, default=PATHS.artifacts)
    indobert.add_argument("--run-id")

    calibrate = subparsers.add_parser(
        "calibrate-indobert", help="Freeze validation-only IndoBERT calibration"
    )
    calibrate.add_argument("--split-dir", type=Path, required=True)
    calibrate.add_argument("--model-run-dir", type=Path, required=True)
    calibrate.add_argument("--output-dir", type=Path, required=True)

    evaluate = subparsers.add_parser(
        "evaluate-indobert", help="Run one frozen locked-test IndoBERT evaluation"
    )
    evaluate.add_argument("--split-dir", type=Path, required=True)
    evaluate.add_argument("--model-run-dir", type=Path, required=True)
    evaluate.add_argument("--calibration", type=Path, required=True)
    evaluate.add_argument("--output-dir", type=Path, required=True)
    evaluate.add_argument("--baseline-metrics-dir", type=Path)
    evaluate.add_argument("--baseline-figure-dir", type=Path)

    infer = subparsers.add_parser("infer-corpus", help="Run restricted A9 full-corpus inference")
    infer.add_argument("--reviews", type=Path, required=True)
    infer.add_argument("--model-dir", type=Path, required=True)
    infer.add_argument("--output-dir", type=Path, required=True)

    aggregate = subparsers.add_parser("aggregate-destinations", help="Aggregate A9 predictions")
    aggregate.add_argument("--predictions-dir", type=Path, required=True)
    aggregate.add_argument("--reviews", type=Path, required=True)
    aggregate.add_argument("--output-dir", type=Path, required=True)

    prioritize = subparsers.add_parser("prioritize-destinations", help="Score A9 priorities")
    prioritize.add_argument("--aggregation-dir", type=Path, required=True)
    prioritize.add_argument("--destinations", type=Path, required=True)
    prioritize.add_argument("--output-dir", type=Path, required=True)

    export = subparsers.add_parser("export-app", help="Write privacy-safe A9 aggregate export")
    export.add_argument("--prioritization-dir", type=Path, required=True)
    export.add_argument("--aggregation-dir", type=Path, required=True)
    export.add_argument("--output-dir", type=Path, required=True)

    snapshot = subparsers.add_parser("snapshot-run", help="Write run environment metadata")
    snapshot.add_argument("--output", type=Path, required=True)

    drive = subparsers.add_parser("bootstrap-drive", help="Create persistent Colab Drive layout")
    drive.add_argument("--root", type=Path, required=True)

    run = subparsers.add_parser("run", help="Run one pipeline stage")
    run.add_argument("stage", choices=[stage.value for stage in Stage])
    run.add_argument("--dataset-dir", type=Path)
    run.add_argument("--output-dir", type=Path, default=PATHS.artifacts / "reports")
    run.add_argument("--figure-dir", type=Path, default=PATHS.artifacts / "figures")
    run.add_argument("--interim-dir", type=Path, default=PATHS.interim)
    run.add_argument("--processed-dir", type=Path, default=PATHS.processed)
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
    if args.command == "quality-figures":
        figures = generate_quality_figures(args.report_dir, args.processed_dir, args.figure_dir)
        print(f"Generated {len(figures)} figures in {args.figure_dir}")
        return 0
    if args.command == "annotation-sample":
        summary = run_annotation_sampling(
            args.processed_dir, args.annotation_dir, args.report_dir
        )
        print(args.report_dir / "annotation_sampling_summary.json")
        print(
            f"Generated {summary['pilot_unique_reviews']} pilot and "
            f"{summary['main_unique_reviews']} main reviews"
        )
        return 0
    if args.command == "annotation-figures":
        figures = generate_annotation_figures(
            args.annotation_dir, args.report_dir, args.figure_dir
        )
        print(f"Generated {len(figures)} figures in {args.figure_dir}")
        return 0
    if args.command == "annotation-validate":
        result = validate_annotation_files(args.paths, args.require_completed)
        print(json.dumps(result, indent=2))
        return 1 if result["invalid_records"] else 0
    if args.command == "annotation-agreement":
        result = evaluate_agreement(args.paths, args.output)
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "freeze-gold":
        result = freeze_gold(
            args.paths, args.adjudicated, args.metrics, args.output
        )
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "silver-annotate":
        result = run_silver_annotation(
            args.processed_dir, args.annotation_dir, args.report_dir
        )
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "silver-validate":
        result = validate_silver_records(args.path)
        print(json.dumps(result, indent=2))
        return 1 if result["invalid_records"] else 0
    if args.command == "silver-figures":
        figures = generate_silver_figures(args.annotation_dir, args.figure_dir)
        print(f"Generated {len(figures)} figures in {args.figure_dir}")
        return 0
    if args.command == "split-silver":
        result = run_split(
            args.processed_dir, args.annotation_dir, args.split_dir, args.report_dir
        )
        print(json.dumps(result["distribution"], indent=2))
        return 0
    if args.command == "train-baselines":
        result = run_baselines(args.split_dir, args.artifact_dir, args.figure_dir)
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "evaluate-gold-baselines":
        result = run_gold_baselines(args.split_dir, args.gold, args.artifact_dir)
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "compare-preliminary-final":
        result = run_preliminary_final_comparison(args.metrics_dir, args.figure_dir)
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "evaluate-gold-indobert":
        result = run_gold_indobert_evaluation(
            args.split_dir, args.model_run_dir, args.calibration_dir, args.gold, args.output_dir
        )
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "train-indobert":
        result = run_indobert_training(args.split_dir, args.artifact_dir, args.run_id)
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "calibrate-indobert":
        result = run_calibration(args.split_dir, args.model_run_dir, args.output_dir)
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "evaluate-indobert":
        result = run_locked_test_evaluation(
            args.split_dir,
            args.model_run_dir,
            args.calibration,
            args.output_dir,
            args.baseline_metrics_dir,
            args.baseline_figure_dir,
        )
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "infer-corpus":
        print(json.dumps(run_inference(args.reviews, args.model_dir, args.output_dir), indent=2))
        return 0
    if args.command == "aggregate-destinations":
        print(json.dumps(
            run_aggregation(args.predictions_dir, args.reviews, args.output_dir), indent=2
        ))
        return 0
    if args.command == "prioritize-destinations":
        print(json.dumps(
            run_prioritization(args.aggregation_dir, args.destinations, args.output_dir), indent=2
        ))
        return 0
    if args.command == "export-app":
        print(json.dumps(
            run_export(args.prioritization_dir, args.aggregation_dir, args.output_dir), indent=2
        ))
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
    if args.command == "run" and args.stage == Stage.EDA.value:
        if args.dataset_dir is None:
            raise SystemExit("--dataset-dir is required for the eda stage")
        summary = run_eda(args.dataset_dir, args.output_dir, args.figure_dir)
        print(args.output_dir / "eda_summary.json")
        print(f"Generated {len(summary['figures'])} figures in {args.figure_dir}")
        return 0
    if args.command == "run" and args.stage == Stage.CLEAN.value:
        if args.dataset_dir is None:
            raise SystemExit("--dataset-dir is required for the clean stage")
        summary = run_cleaning(args.dataset_dir, args.interim_dir, args.output_dir)
        print(args.output_dir / "cleaning_summary.json")
        print(f"Generated {len(summary['outputs'])} interim artifacts in {args.interim_dir}")
        return 0
    if args.command == "run" and args.stage == Stage.RESOLVE_ENTITIES.value:
        summary = run_entity_resolution(args.interim_dir, args.processed_dir, args.output_dir)
        print(args.output_dir / "entity_resolution_summary.json")
        print(f"Generated {len(summary['outputs'])} processed artifacts in {args.processed_dir}")
        return 0
    if args.command == "run" and args.stage == Stage.SPLIT.value:
        result = run_split(
            args.processed_dir, PATHS.annotations, PATHS.splits, args.output_dir
        )
        print(json.dumps(result["distribution"], indent=2))
        return 0
    if args.command == "run" and args.stage in {
        Stage.TRAIN_KEYWORD.value,
        Stage.TRAIN_TFIDF.value,
    }:
        result = run_baselines(PATHS.splits, PATHS.artifacts, args.figure_dir)
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "run" and args.stage == Stage.TRAIN_INDOBERT.value:
        result = run_indobert_training(PATHS.splits, PATHS.artifacts)
        print(json.dumps(result, indent=2))
        return 0
    if args.command == "run" and args.stage in {Stage.CALIBRATE.value, Stage.EVALUATE.value}:
        raise SystemExit(
            "Use calibrate-indobert or evaluate-indobert with explicit model and artifact paths"
        )
    if args.command == "run" and args.stage in {
        Stage.INFER.value, Stage.AGGREGATE.value, Stage.PRIORITIZE.value, Stage.EXPORT_APP.value,
    }:
        raise SystemExit("Use the explicit A9 command with immutable input and output paths")
    raise NotImplementedError(
        f"Stage '{args.stage}' is declared but not implemented. "
        "Implement and test the stage before marking its TODO complete."
    )


if __name__ == "__main__":
    raise SystemExit(main())

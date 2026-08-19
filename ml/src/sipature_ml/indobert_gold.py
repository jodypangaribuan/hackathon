"""Inference-only IndoBERT evaluation against human-gold labels.

The A7 IndoBERT model (aspect + aspect-conditioned polarity) was trained on
silver train/validation. This module evaluates that already-trained model
against the human-gold reference (``gold.jsonl``) without retraining or
re-tuning: it reuses the frozen calibration (temperature + detection thresholds
derived on silver validation) and applies it to the gold test split.

This is a separate, human-verified reference and does NOT reopen the locked
silver test. It mirrors ``evaluate-gold-baselines`` (keyword/TF-IDF) so all three
models are compared against the same gold test.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from .config import load_config
from .evaluation import (
    _infer_local_models,
    aspect_metrics,
    polarity_metrics,
    sigmoid,
    validate_model_contract,
)
from .gold_baselines import build_gold_split_records, load_gold_labels
from .indobert import build_aspect_targets, build_polarity_instances
from .manifest import sha256_file

MANIFEST_NAME = "split_manifest_silver_v1.json"


def run_gold_indobert_evaluation(
    split_dir: Path,
    model_run_dir: Path,
    calibration_dir: Path,
    gold_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Evaluate the frozen A7 IndoBERT against gold labels (no retrain/re-tune)."""
    config = load_config("training")
    labels = sorted(load_config("taxonomy")["aspect_definitions"])

    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite immutable output: {output_dir}")

    calibration_path = calibration_dir / "calibration.json"
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    temperature = float(calibration["temperature"])
    detection = [calibration["detection_thresholds"][label] for label in labels]

    a7_manifest_path = model_run_dir / "manifest.json"
    a7_manifest = json.loads(a7_manifest_path.read_text(encoding="utf-8"))
    validate_model_contract(model_run_dir, a7_manifest)
    if a7_manifest.get("model", {}).get("id") != config["indobert"]["model_id"]:
        raise ValueError("Current IndoBERT model ID differs from A7 manifest")

    gold_labels = load_gold_labels(gold_path)
    split_records = build_gold_split_records(split_dir, gold_labels)
    test_records = split_records["test"]

    targets = np.asarray(build_aspect_targets(test_records, labels), dtype=int)
    section = config["calibration"]
    inference = _infer_local_models(
        test_records,
        model_run_dir,
        config["indobert"]["max_length"],
        section["inference_batch_size"],
        section["require_cuda"],
    )
    logits = np.asarray(inference["aspect_logits"], dtype=float)
    probabilities = sigmoid(logits / temperature)
    polarity_instances = build_polarity_instances(test_records)
    polarity_logits = np.asarray(inference["polarity_logits"], dtype=float)
    if logits.shape != targets.shape or len(polarity_logits) != len(polarity_instances):
        raise ValueError("Inference output shape does not match gold references")

    aspect = aspect_metrics(
        targets, probabilities, detection, labels,
        latency_seconds=inference.get("aspect_latency_seconds"),
    )
    polarity = polarity_metrics(
        [row["label"] for row in polarity_instances], np.argmax(polarity_logits, axis=1)
    )

    metrics = {
        "model_version": "indobert-aspect-gold-v1",
        "reference_label_type": "human_gold",
        "phase": "gold_inference_only_evaluation",
        "evaluation_basis": "silver-trained A7 IndoBERT, frozen silver-validation calibration (no retrain/re-tune)",
        "gold_sha256": sha256_file(gold_path),
        "split_version": json.loads(
            (split_dir / MANIFEST_NAME).read_text(encoding="utf-8")
        )["split_version"],
        "a7_run_id": model_run_dir.name,
        "macro_f1": aspect["macro_f1"],
        "micro_f1": aspect["micro_f1"],
        "per_aspect": aspect["per_label"],
        "aspect_latency_ms_per_review": aspect["latency"]["milliseconds_per_record"],
        "polarity": polarity,
        "calibration": {
            "temperature": temperature,
            "threshold_source": str(calibration_path),
            "calibration_sha256": sha256_file(calibration_path),
        },
        "severity": {"status": "unavailable_no_model"},
    }

    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    comparison_metrics = {
        "model_version": metrics["model_version"],
        "reference_label_type": metrics["reference_label_type"],
        "macro_f1": metrics["macro_f1"],
        "micro_f1": metrics["micro_f1"],
        "records": len(test_records),
        "per_aspect": metrics["per_aspect"],
        "polarity_macro_f1": polarity["macro_f1"],
        "evaluation_basis": metrics["evaluation_basis"],
        "gold_sha256": metrics["gold_sha256"],
        "a7_run_id": model_run_dir.name,
    }
    (output_dir / "indobert-gold-v1-test-metrics.json").write_text(
        json.dumps(comparison_metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "phase": "gold_inference_only_evaluation",
        "reference_label_type": "human_gold",
        "gold_sha256": sha256_file(gold_path),
        "a7_manifest_sha256": sha256_file(a7_manifest_path),
        "calibration_sha256": sha256_file(calibration_path),
        "split_manifest_sha256": sha256_file(split_dir / MANIFEST_NAME),
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return metrics

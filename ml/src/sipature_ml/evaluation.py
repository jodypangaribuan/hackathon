"""Validation calibration and one-shot locked-test evaluation for IndoBERT."""

from __future__ import annotations

import csv
import hashlib
import json
import time
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score

from .config import ML_ROOT, load_config
from .indobert import POLARITY_LABELS, build_aspect_targets, build_polarity_instances, read_jsonl
from .manifest import sha256_file

MODEL_HASH_KEYS = (
    "aspect/model/model.safetensors",
    "polarity/model/model.safetensors",
)
MANIFEST_NAME = "split_manifest_silver_v1.json"


def sigmoid(values: Sequence[float] | np.ndarray) -> np.ndarray:
    """Compute a numerically stable sigmoid."""

    values = np.asarray(values, dtype=float)
    result = np.empty_like(values)
    positive = values >= 0
    result[positive] = 1.0 / (1.0 + np.exp(-values[positive]))
    exponential = np.exp(values[~positive])
    result[~positive] = exponential / (1.0 + exponential)
    return result


def softmax(values: Sequence[Sequence[float]] | np.ndarray) -> np.ndarray:
    """Compute a numerically stable softmax over the final axis."""

    values = np.asarray(values, dtype=float)
    shifted = values - np.max(values, axis=-1, keepdims=True)
    exponential = np.exp(shifted)
    return exponential / exponential.sum(axis=-1, keepdims=True)


def multilabel_nll(logits: np.ndarray, targets: np.ndarray, temperature: float = 1.0) -> float:
    """Return mean binary negative log likelihood for multilabel logits."""

    scaled = np.asarray(logits, dtype=float) / temperature
    targets = np.asarray(targets, dtype=float)
    if scaled.shape != targets.shape or scaled.ndim != 2:
        raise ValueError("Logits and targets must be equal non-empty 2D matrices")
    losses = np.maximum(scaled, 0) - scaled * targets + np.log1p(np.exp(-np.abs(scaled)))
    return float(losses.mean())


def fit_multilabel_temperature(
    logits: np.ndarray,
    targets: np.ndarray,
    lower: float = 0.5,
    upper: float = 5.0,
    grid_size: int = 181,
) -> dict[str, float]:
    """Fit one temperature on validation using a deterministic bounded grid."""

    if lower <= 0 or upper < lower or grid_size < 2:
        raise ValueError("Invalid temperature grid")
    before = multilabel_nll(logits, targets)
    candidates = np.linspace(lower, upper, grid_size)
    scored = [(multilabel_nll(logits, targets, float(value)), float(value)) for value in candidates]
    after, temperature = min(scored, key=lambda item: (item[0], abs(item[1] - 1.0), item[1]))
    if after > before:
        temperature, after = 1.0, before
    return {"temperature": temperature, "nll_before": before, "nll_after": after}


def expected_calibration_error(
    probabilities: np.ndarray, targets: np.ndarray, bins: int = 10
) -> float:
    """Calculate equal-width ECE over flattened multilabel decisions."""

    probabilities = np.asarray(probabilities, dtype=float).ravel()
    targets = np.asarray(targets, dtype=float).ravel()
    if probabilities.shape != targets.shape or not len(probabilities) or bins <= 0:
        raise ValueError("Probabilities/targets must align and bins must be positive")
    if np.any((probabilities < 0) | (probabilities > 1)):
        raise ValueError("Probabilities must be in [0, 1]")
    indices = np.minimum((probabilities * bins).astype(int), bins - 1)
    error = 0.0
    for index in range(bins):
        selected = indices == index
        if selected.any():
            error += selected.mean() * abs(probabilities[selected].mean() - targets[selected].mean())
    return float(error)


def multilabel_brier_score(probabilities: np.ndarray, targets: np.ndarray) -> float:
    """Calculate mean squared probability error over all labels and examples."""

    probabilities = np.asarray(probabilities, dtype=float)
    targets = np.asarray(targets, dtype=float)
    if probabilities.shape != targets.shape or probabilities.ndim != 2 or not len(probabilities):
        raise ValueError("Probabilities and targets must be equal non-empty 2D matrices")
    return float(np.mean((probabilities - targets) ** 2))


def tune_detection_thresholds(
    probabilities: np.ndarray,
    targets: np.ndarray,
    candidates: Sequence[float],
) -> np.ndarray:
    """Maximize per-label F1; ties choose the lowest threshold for deterministic recall."""

    probabilities = np.asarray(probabilities, dtype=float)
    targets = np.asarray(targets, dtype=int)
    ordered = sorted({float(value) for value in candidates})
    if probabilities.shape != targets.shape or probabilities.ndim != 2 or not ordered:
        raise ValueError("Invalid threshold tuning inputs")
    thresholds = []
    for index in range(probabilities.shape[1]):
        scores = [
            f1_score(targets[:, index], probabilities[:, index] >= value, zero_division=0)
            for value in ordered
        ]
        thresholds.append(ordered[int(np.argmax(scores))])
    return np.asarray(thresholds)


def tune_alert_thresholds(
    probabilities: np.ndarray,
    targets: np.ndarray,
    candidates: Sequence[float],
    minimum_predictions: int,
    minimum_precision: float = 0.8,
) -> list[dict[str, Any]]:
    """Choose precision-first alert thresholds with support, then recall/tie ordering."""

    probabilities = np.asarray(probabilities, dtype=float)
    targets = np.asarray(targets, dtype=int)
    ordered = sorted({float(value) for value in candidates})
    if minimum_predictions <= 0 or not 0 <= minimum_precision <= 1:
        raise ValueError("Invalid alert constraints")
    results = []
    for index in range(probabilities.shape[1]):
        choices = []
        for threshold in ordered:
            predicted = probabilities[:, index] >= threshold
            support = int(predicted.sum())
            if support < minimum_predictions:
                continue
            precision = float(precision_score(targets[:, index], predicted, zero_division=0))
            recall = float(recall_score(targets[:, index], predicted, zero_division=0))
            choices.append((precision, recall, threshold, support))
        eligible = [item for item in choices if item[0] >= minimum_precision]
        pool = eligible or choices
        if not pool:
            results.append({"threshold": None, "precision": None, "recall": None, "predicted_support": 0, "target_met": False})
            continue
        precision, recall, threshold, support = max(pool, key=lambda item: (item[0], item[1], item[2]))
        results.append({"threshold": threshold, "precision": precision, "recall": recall,
                        "predicted_support": support, "target_met": precision >= minimum_precision})
    return results


def aspect_metrics(
    targets: np.ndarray,
    probabilities: np.ndarray,
    thresholds: Sequence[float],
    labels: Sequence[str],
    alert_thresholds: Sequence[float | None] | None = None,
    latency_seconds: float | None = None,
) -> dict[str, Any]:
    """Build macro/micro/per-label detection metrics and alert precision."""

    targets = np.asarray(targets, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    predicted = probabilities >= np.asarray(thresholds, dtype=float)
    if targets.shape != probabilities.shape or targets.shape[1] != len(labels):
        raise ValueError("Metric dimensions do not match labels")
    per_label = {}
    for index, label in enumerate(labels):
        per_label[label] = {
            "f1": float(f1_score(targets[:, index], predicted[:, index], zero_division=0)),
            "precision": float(precision_score(targets[:, index], predicted[:, index], zero_division=0)),
            "recall": float(recall_score(targets[:, index], predicted[:, index], zero_division=0)),
            "support": int(targets[:, index].sum()),
            "predicted_support": int(predicted[:, index].sum()),
        }
    alerts = {}
    for index, label in enumerate(labels):
        threshold = None if alert_thresholds is None else alert_thresholds[index]
        if threshold is None:
            alerts[label] = {"threshold": None, "precision": None, "predicted_support": 0}
        else:
            alert = probabilities[:, index] >= threshold
            alerts[label] = {"threshold": float(threshold),
                             "precision": float(precision_score(targets[:, index], alert, zero_division=0)),
                             "predicted_support": int(alert.sum())}
    return {
        "macro_f1": float(f1_score(targets, predicted, average="macro", zero_division=0)),
        "micro_f1": float(f1_score(targets, predicted, average="micro", zero_division=0)),
        "per_label": per_label,
        "precision_at_alert": alerts,
        "latency": {"total_seconds": latency_seconds,
                    "milliseconds_per_record": None if latency_seconds is None else latency_seconds * 1000 / len(targets)},
    }


def polarity_metrics(targets: Sequence[int], predicted: Sequence[int]) -> dict[str, Any]:
    """Calculate polarity Macro F1 and a fixed-order confusion matrix."""

    targets = np.asarray(targets, dtype=int)
    predicted = np.asarray(predicted, dtype=int)
    if targets.shape != predicted.shape:
        raise ValueError("Polarity targets and predictions must align")
    if not len(targets):
        return {
            "macro_f1": 0.0,
            "confusion_matrix": np.zeros((len(POLARITY_LABELS), len(POLARITY_LABELS)), dtype=int).tolist(),
            "labels": list(POLARITY_LABELS),
            "support": 0,
        }
    return {
        "macro_f1": float(f1_score(targets, predicted, labels=range(len(POLARITY_LABELS)),
                                   average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(
            targets, predicted, labels=range(len(POLARITY_LABELS))
        ).tolist(),
        "labels": list(POLARITY_LABELS),
        "support": len(targets),
    }


def build_error_cases(
    records: Sequence[dict[str, Any]],
    labels: Sequence[str],
    targets: np.ndarray,
    probabilities: np.ndarray,
    thresholds: Sequence[float],
) -> list[dict[str, Any]]:
    """Build all aggregate FP/FN cases with explicitly manual linguistic fields."""

    predicted = np.asarray(probabilities) >= np.asarray(thresholds)
    cases = []
    for row_index, record in enumerate(records):
        for label_index, label in enumerate(labels):
            actual = bool(targets[row_index, label_index])
            estimate = bool(predicted[row_index, label_index])
            if actual == estimate:
                continue
            cases.append({
                "review_id": record["review_id"],
                "destination_id": record.get("destination_id"),
                "text": record.get("text", ""),
                "aspect": label,
                "error_type": "FN" if actual else "FP",
                "probability": float(probabilities[row_index, label_index]),
                "threshold": float(thresholds[label_index]),
                "manual_audit_status": "pending",
                "manual_linguistic_category": "",
                "manual_negation": "",
                "manual_reputational_risk": "",
                "manual_notes": "",
            })
    return sorted(cases, key=lambda row: (row["error_type"], row["aspect"], row["review_id"]))


def validate_model_contract(model_run_dir: Path, manifest: dict[str, Any]) -> dict[str, str]:
    """Verify A7's final aspect/polarity model files against its full manifest."""

    hashes = manifest.get("artifact_hashes")
    if not isinstance(hashes, dict):
        raise TypeError("A7 manifest has no artifact_hashes mapping")
    verified = {}
    for key in MODEL_HASH_KEYS:
        expected = hashes.get(key)
        if not isinstance(expected, str):
            raise TypeError(f"A7 manifest is missing model hash: {key}")
        actual = sha256_file(model_run_dir / key)
        if actual != expected:
            raise ValueError(f"A7 model hash mismatch: {key}")
        verified[key] = actual
    return verified


def validate_calibration_contract(
    calibration: dict[str, Any], calibration_sha256: str, model_hashes: dict[str, str]
) -> None:
    """Validate a frozen calibration's self-hash marker and A7 model binding."""

    if calibration.get("artifact_sha256") != calibration_sha256:
        raise ValueError("Calibration hash does not match frozen manifest")
    if calibration.get("model_hashes") != model_hashes:
        raise ValueError("Calibration model hashes do not match A7 models")


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def _load_a7_contract(model_run_dir: Path, config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    manifest_path = model_run_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    hashes = validate_model_contract(model_run_dir, manifest)
    if manifest.get("model", {}).get("id") != config["indobert"]["model_id"]:
        raise ValueError("Current IndoBERT model ID differs from A7 manifest")
    if manifest.get("model", {}).get("revision") != config["indobert"]["revision"]:
        raise ValueError("Current IndoBERT revision differs from A7 manifest")
    return manifest, hashes


def _infer_local_models(
    records: Sequence[dict[str, Any]], model_run_dir: Path, max_length: int
) -> dict[str, Any]:
    """Infer aspects and gold-aspect-conditioned polarity from local A7 files only."""

    try:
        import torch
        from transformers import BertForSequenceClassification, BertTokenizer
    except ImportError as error:
        raise RuntimeError("Install the A8 train dependencies in the Colab runtime") from error

    def infer(model_dir: Path, texts: list[str]) -> np.ndarray:
        tokenizer = BertTokenizer.from_pretrained(model_dir, local_files_only=True)
        model = BertForSequenceClassification.from_pretrained(model_dir, local_files_only=True)
        model.eval()
        batches = []
        with torch.no_grad():
            for start in range(0, len(texts), 32):
                encoded = tokenizer(texts[start:start + 32], return_tensors="pt", padding=True,
                                    truncation=True, max_length=max_length)
                batches.append(model(**encoded).logits.detach().cpu().numpy())
        return np.concatenate(batches) if batches else np.empty((0, model.config.num_labels))

    polarity = build_polarity_instances(records)
    started = time.perf_counter()
    aspect_logits = infer(model_run_dir / "aspect" / "model", [row["text"] for row in records])
    polarity_logits = infer(model_run_dir / "polarity" / "model",
                            [row["conditioned_text"] for row in polarity])
    return {"aspect_logits": aspect_logits, "polarity_logits": polarity_logits,
            "latency_seconds": time.perf_counter() - started}


def _preflight_output(output_dir: Path) -> None:
    if output_dir.exists():
        raise FileExistsError(f"Refusing to overwrite immutable output: {output_dir}")


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _artifact_hashes(output_dir: Path) -> dict[str, str]:
    return {str(path.relative_to(output_dir)): sha256_file(path)
            for path in sorted(output_dir.rglob("*")) if path.is_file() and path.name != "manifest.json"}


def _plot_calibration(targets: np.ndarray, before: np.ndarray, after: np.ndarray, output: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axis = plt.subplots(figsize=(6, 4))
    axis.bar(["Before", "After"], [multilabel_brier_score(before, targets),
                                    multilabel_brier_score(after, targets)], color=["#8B95A5", "#157A6E"])
    axis.set_ylabel("Multilabel Brier score")
    axis.set_title("Aspect Calibration", loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def run_calibration(
    split_dir: Path,
    model_run_dir: Path,
    output_dir: Path,
    *,
    inference_fn: Callable[[Sequence[dict[str, Any]], Path, int], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Calibrate on validation only; this function never resolves or reads test."""

    _preflight_output(output_dir)
    config = load_config("training")
    section = config["calibration"]
    split_manifest_path = split_dir / MANIFEST_NAME
    split_manifest = json.loads(split_manifest_path.read_text(encoding="utf-8"))
    validation_entry = split_manifest.get("outputs", {}).get("validation")
    if not isinstance(validation_entry, dict):
        raise TypeError("Locked manifest has no validation entry")
    validation_path = split_dir / validation_entry["path"]
    validation_hash = sha256_file(validation_path)
    if validation_hash != validation_entry["sha256"]:
        raise ValueError("Validation hash mismatch")
    a7_manifest, model_hashes = _load_a7_contract(model_run_dir, config)
    if a7_manifest.get("input_hashes", {}).get("validation") != validation_hash:
        raise ValueError("A7 validation hash differs from locked validation")
    records = read_jsonl(validation_path)
    labels = sorted(load_config("taxonomy")["aspect_definitions"])
    targets = np.asarray(build_aspect_targets(records, labels), dtype=int)
    inference = (inference_fn or _infer_local_models)(records, model_run_dir, config["indobert"]["max_length"])
    logits = np.asarray(inference["aspect_logits"], dtype=float)
    polarity_instances = build_polarity_instances(records)
    polarity_logits = np.asarray(inference["polarity_logits"], dtype=float)
    if logits.shape != targets.shape:
        raise ValueError("Aspect inference shape does not match validation targets")
    if len(polarity_logits) != len(polarity_instances):
        raise ValueError("Polarity inference shape does not match validation instances")
    fit = fit_multilabel_temperature(logits, targets, section["temperature_min"],
                                     section["temperature_max"], section["temperature_grid_size"])
    before, after = sigmoid(logits), sigmoid(logits / fit["temperature"])
    detection = tune_detection_thresholds(after, targets, section["threshold_candidates"])
    alerts = tune_alert_thresholds(after, targets, section["threshold_candidates"],
                                   section["alert_minimum_predictions"], section["alert_minimum_precision"])
    output_dir.mkdir(parents=True)
    calibration = {
        "version": section["version"], "output_version": section["output_version"],
        "created_at": datetime.now(timezone.utc).isoformat(), "phase": "validation_calibration",
        "test_read": False, "labels": labels, "temperature": fit["temperature"],
        "detection_thresholds": dict(zip(labels, detection.tolist())),
        "alert_thresholds": {label: value["threshold"] for label, value in zip(labels, alerts)},
        "alert_validation": dict(zip(labels, alerts)), "validation_sha256": validation_hash,
        "split_manifest_sha256": sha256_file(split_manifest_path),
        "a7_manifest_sha256": sha256_file(model_run_dir / "manifest.json"),
        "a7_training_config_sha256": a7_manifest.get("training_config_sha256"),
        "current_training_config_sha256": sha256_file(ML_ROOT / "configs" / "training.yaml"),
        "indobert_config_canonical_sha256": _canonical_hash(config["indobert"]),
        "calibration_config": section, "calibration_config_canonical_sha256": _canonical_hash(section),
        "model_hashes": model_hashes,
        "validation_calibration": {
            **fit, "ece_before": expected_calibration_error(before, targets, section["ece_bins"]),
            "ece_after": expected_calibration_error(after, targets, section["ece_bins"]),
            "brier_before": multilabel_brier_score(before, targets),
            "brier_after": multilabel_brier_score(after, targets),
        },
        "validation_polarity": polarity_metrics(
            [row["label"] for row in polarity_instances], np.argmax(polarity_logits, axis=1)
        ),
    }
    calibration_path = output_dir / "calibration.json"
    _write_json(calibration_path, calibration)
    np.savez_compressed(output_dir / "validation-predictions.npz", logits=logits, targets=targets,
                        probabilities=after, polarity_logits=polarity_logits)
    _plot_calibration(targets, before, after, output_dir / "calibration.png")
    manifest = {"phase": "validation_calibration", "test_read": False,
                "calibration_sha256": sha256_file(calibration_path), "artifact_hashes": _artifact_hashes(output_dir)}
    _write_json(output_dir / "manifest.json", manifest)
    return calibration


def _resolve_calibration(calibration_dir_or_file: Path) -> tuple[Path, Path]:
    if calibration_dir_or_file.is_dir():
        return calibration_dir_or_file / "calibration.json", calibration_dir_or_file / "manifest.json"
    return calibration_dir_or_file, calibration_dir_or_file.parent / "manifest.json"


def _load_baseline_metrics(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    candidates = [path] if path.is_file() else sorted(path.glob("*.json"))
    return {item.name: json.loads(item.read_text(encoding="utf-8")) for item in candidates}


def _write_errors(output_dir: Path, cases: list[dict[str, Any]]) -> None:
    _write_json(output_dir / "errors.json", cases)
    fields = list(cases[0]) if cases else ["review_id", "aspect", "error_type"]
    with (output_dir / "errors.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(cases)
    for error_type in ("FP", "FN"):
        queue = [row for row in cases if row["error_type"] == error_type][:50]
        _write_json(output_dir / f"audit-{error_type.lower()}.json", queue)


def _plot_test_figures(metrics: dict[str, Any], probabilities: np.ndarray, targets: np.ndarray,
                       output_dir: Path, baseline: dict[str, Any] | None) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    matrix = np.asarray(metrics["polarity"]["confusion_matrix"])
    fig, axis = plt.subplots(figsize=(5, 4))
    image = axis.imshow(matrix, cmap="Blues")
    axis.set_xticks(range(3), POLARITY_LABELS)
    axis.set_yticks(range(3), POLARITY_LABELS)
    axis.set_xlabel("Predicted")
    axis.set_ylabel("Reference")
    fig.colorbar(image, ax=axis)
    fig.tight_layout()
    fig.savefig(output_dir / "polarity-confusion-matrix.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    labels = list(metrics["aspect"]["per_label"])
    fig, axis = plt.subplots(figsize=(9, 5))
    axis.bar(labels, [metrics["aspect"]["per_label"][label]["f1"] for label in labels])
    axis.tick_params(axis="x", rotation=70)
    axis.set_ylim(0, 1)
    axis.set_ylabel("F1")
    fig.tight_layout()
    fig.savefig(output_dir / "aspect-per-label-f1.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    _plot_calibration(targets, probabilities, probabilities, output_dir / "test-calibration.png")
    fig, axis = plt.subplots(figsize=(6, 4))
    axis.bar(["IndoBERT"], [metrics["aspect"]["macro_f1"]], color="#157A6E")
    axis.set_ylim(0, 1)
    axis.set_title("Baseline comparison" if baseline else "IndoBERT result (no baseline supplied)")
    fig.tight_layout()
    fig.savefig(output_dir / "comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def run_locked_test_evaluation(
    split_dir: Path,
    model_run_dir: Path,
    calibration_dir_or_file: Path,
    output_dir: Path,
    baseline_metrics_dir: Path | None = None,
    baseline_figure_dir: Path | None = None,
    *,
    inference_fn: Callable[[Sequence[dict[str, Any]], Path, int], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Evaluate the locked test once using frozen validation-derived calibration."""

    _preflight_output(output_dir)
    config = load_config("training")
    split_manifest_path = split_dir / MANIFEST_NAME
    split_manifest = json.loads(split_manifest_path.read_text(encoding="utf-8"))
    if split_manifest.get("test_is_locked") is not True:
        raise ValueError("Split manifest does not declare a locked test")
    calibration_path, calibration_manifest_path = _resolve_calibration(calibration_dir_or_file)
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    calibration_manifest = json.loads(calibration_manifest_path.read_text(encoding="utf-8"))
    calibration_hash = sha256_file(calibration_path)
    if calibration_manifest.get("calibration_sha256") != calibration_hash:
        raise ValueError("Frozen calibration hash mismatch")
    _a7_manifest, model_hashes = _load_a7_contract(model_run_dir, config)
    frozen = dict(calibration)
    frozen["artifact_sha256"] = calibration_manifest["calibration_sha256"]
    validate_calibration_contract(frozen, calibration_hash, model_hashes)
    if calibration.get("a7_manifest_sha256") != sha256_file(model_run_dir / "manifest.json"):
        raise ValueError("Calibration was frozen against a different A7 manifest")
    if calibration.get("calibration_config_canonical_sha256") != _canonical_hash(config["calibration"]):
        raise ValueError("Current calibration configuration differs from frozen calibration")
    if calibration.get("indobert_config_canonical_sha256") != _canonical_hash(config["indobert"]):
        raise ValueError("Current IndoBERT configuration differs from frozen calibration")
    test_entry = split_manifest.get("outputs", {}).get("test")
    if not isinstance(test_entry, dict):
        raise TypeError("Locked manifest has no test entry")
    test_path = split_dir / test_entry["path"]
    test_hash = sha256_file(test_path)
    if test_hash != test_entry["sha256"]:
        raise ValueError("Locked test hash mismatch")
    records = read_jsonl(test_path)
    labels = calibration["labels"]
    targets = np.asarray(build_aspect_targets(records, labels), dtype=int)
    inference = (inference_fn or _infer_local_models)(records, model_run_dir, config["indobert"]["max_length"])
    logits = np.asarray(inference["aspect_logits"], dtype=float)
    probabilities = sigmoid(logits / calibration["temperature"])
    polarity_instances = build_polarity_instances(records)
    polarity_logits = np.asarray(inference["polarity_logits"], dtype=float)
    if logits.shape != targets.shape or len(polarity_logits) != len(polarity_instances):
        raise ValueError("Inference output shape does not match locked references")
    detection = [calibration["detection_thresholds"][label] for label in labels]
    alerts = [calibration["alert_thresholds"][label] for label in labels]
    baseline = _load_baseline_metrics(baseline_metrics_dir)
    metrics = {
        "phase": "locked_test_evaluation", "test_inference_passes": 1,
        "reference_label_type": split_manifest.get("reference_label_type"),
        "aspect": aspect_metrics(targets, probabilities, detection, labels, alerts,
                                 float(inference.get("latency_seconds", 0.0))),
        "calibration": {"ece": expected_calibration_error(probabilities, targets, config["calibration"]["ece_bins"]),
                        "brier": multilabel_brier_score(probabilities, targets)},
        "polarity": polarity_metrics([row["label"] for row in polarity_instances],
                                     np.argmax(polarity_logits, axis=1)),
        "polarity_evaluation_basis": "gold_or_silver_annotated_aspects_not_predicted_aspects",
        "severity": {"status": "unavailable_no_model"},
        "baseline_comparison": baseline,
        "baseline_figure_dir": None if baseline_figure_dir is None else str(baseline_figure_dir),
    }
    cases = build_error_cases(records, labels, targets, probabilities, detection)
    output_dir.mkdir(parents=True)
    _write_json(output_dir / "metrics.json", metrics)
    np.savez_compressed(output_dir / "test-predictions.npz", logits=logits, targets=targets,
                        probabilities=probabilities, polarity_logits=polarity_logits)
    _write_errors(output_dir, cases)
    _plot_test_figures(metrics, probabilities, targets, output_dir, baseline)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(), "phase": "locked_test_evaluation",
        "test_inference_passes": 1, "test_sha256": test_hash,
        "split_manifest_sha256": sha256_file(split_manifest_path),
        "calibration_sha256": calibration_hash,
        "a7_manifest_sha256": sha256_file(model_run_dir / "manifest.json"),
        "model_hashes": model_hashes, "artifact_hashes": _artifact_hashes(output_dir),
        "manual_error_policy": "No automatic linguistic category classification; audit fields remain pending.",
    }
    _write_json(output_dir / "manifest.json", manifest)
    return metrics

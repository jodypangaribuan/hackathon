"""Train/validation-only IndoBERT task pipeline for GPU execution.

The module deliberately imports torch and transformers only inside training and
reload functions. Pure data, configuration, hash, and schema helpers therefore
remain usable in the CPU development profile.
"""

from __future__ import annotations

import json
import math
import random
from collections import Counter
from collections.abc import Iterable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import f1_score

from .config import ML_ROOT, load_config
from .environment import build_environment_snapshot
from .manifest import sha256_file

MODEL_ID = "indobenchmark/indobert-base-p1"
MODEL_REVISION = "c2cd0b51ddce6580eb35263b39b0a1e5fb0a39e2"
MODEL_LICENSE = "MIT"
MODEL_PARAMETERS = 124_500_000
TOKENIZER_DESCRIPTION = "BertTokenizer (WordPiece)"
POLARITY_LABELS = ("positive", "negative", "neutral")
SEVERITY_LABELS = ("low", "medium", "high")
TRAINING_SPLITS = ("train", "validation")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL file. Callers must first enforce the split allowlist."""

    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def validate_indobert_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate A7 configuration and reject an unpinned or incompatible model."""

    required = {
        "model_id", "revision", "license", "parameter_count", "tokenizer", "max_length",
        "batch_size", "gradient_accumulation_steps", "learning_rate", "weight_decay",
        "epochs", "warmup_ratio", "early_stopping_patience", "mixed_precision",
        "aspect_loss", "classification_loss", "severity_min_train_per_class",
        "severity_min_validation_per_class", "output_version",
    }
    section = config.get("indobert")
    if not isinstance(section, dict):
        raise TypeError("training.indobert must be a mapping")
    missing = sorted(required - section.keys())
    if missing:
        raise ValueError(f"Missing IndoBERT config keys: {', '.join(missing)}")
    expected = {
        "model_id": MODEL_ID,
        "revision": MODEL_REVISION,
        "license": MODEL_LICENSE,
        "parameter_count": MODEL_PARAMETERS,
        "tokenizer": TOKENIZER_DESCRIPTION,
        "aspect_loss": "weighted_bce",
        "classification_loss": "weighted_cross_entropy",
    }
    for key, value in expected.items():
        if section[key] != value:
            raise ValueError(f"indobert.{key} must be {value!r}")
    for key in ("max_length", "batch_size", "gradient_accumulation_steps", "epochs"):
        if not isinstance(section[key], int) or section[key] <= 0:
            raise ValueError(f"indobert.{key} must be a positive integer")
    for key in ("learning_rate", "weight_decay", "warmup_ratio"):
        if not isinstance(section[key], (int, float)) or section[key] < 0:
            raise ValueError(f"indobert.{key} must be non-negative")
    if section["mixed_precision"] not in {"fp16", "bf16", "none"}:
        raise ValueError("indobert.mixed_precision must be fp16, bf16, or none")
    if not isinstance(config.get("seed"), int):
        raise TypeError("training.seed must be an integer")
    return section


def token_length_summary(lengths: Sequence[int], max_length: int) -> dict[str, Any]:
    """Summarize tokenizer lengths and coverage without inspecting locked test data."""

    if not lengths or any(length <= 0 for length in lengths):
        raise ValueError("Token lengths must contain positive values")
    ordered = np.sort(np.asarray(lengths, dtype=int))

    def percentile(value: float) -> int:
        index = min(len(ordered) - 1, math.ceil(value * len(ordered)) - 1)
        return int(ordered[index])

    covered = int((ordered <= max_length).sum())
    return {
        "records": len(ordered),
        "max_length": max_length,
        "p50_tokens": percentile(0.50),
        "p90_tokens": percentile(0.90),
        "p95_tokens": percentile(0.95),
        "p99_tokens": percentile(0.99),
        "maximum_tokens": int(ordered[-1]),
        "records_within_max_length": covered,
        "coverage_at_max_length": covered / len(ordered),
    }


def verify_training_split_hashes(split_dir: Path, manifest: dict[str, Any]) -> dict[str, str]:
    """Verify only train and validation against the manifest, never opening test."""

    outputs = manifest.get("outputs", {})
    verified: dict[str, str] = {}
    for split in TRAINING_SPLITS:
        entry = outputs.get(split)
        if not isinstance(entry, dict) or not {"path", "sha256"} <= entry.keys():
            raise ValueError(f"Manifest has no complete {split} output entry")
        path = split_dir / entry["path"]
        digest = sha256_file(path)
        if digest != entry["sha256"]:
            raise ValueError(f"Split hash mismatch: {split}")
        verified[split] = digest
    return verified


def load_training_records(split_dir: Path, manifest_path: Path) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], dict[str, str]]:
    """Load hash-verified train/validation data without resolving the test filename."""

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    hashes = verify_training_split_hashes(split_dir, manifest)
    records = {
        split: read_jsonl(split_dir / manifest["outputs"][split]["path"])
        for split in TRAINING_SPLITS
    }
    return records, manifest, hashes


def build_aspect_targets(records: Sequence[dict[str, Any]], aspects: Sequence[str]) -> list[list[float]]:
    """Create one multilabel vector per review in the supplied taxonomy order."""

    index = {label: position for position, label in enumerate(aspects)}
    targets: list[list[float]] = []
    for record in records:
        row = [0.0] * len(aspects)
        for label in record.get("labels", []):
            if label["aspect"] not in index:
                raise ValueError(f"Unknown aspect: {label['aspect']}")
            row[index[label["aspect"]]] = 1.0
        targets.append(row)
    return targets


def build_polarity_instances(records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create one aspect-conditioned polarity example per annotated aspect."""

    return [
        {
            "review_id": record["review_id"],
            "text": record["text"],
            "aspect": label["aspect"],
            "conditioned_text": f"[ASPECT] {label['aspect']} [REVIEW] {record['text']}",
            "label": POLARITY_LABELS.index(label["polarity"]),
        }
        for record in records
        for label in record.get("labels", [])
    ]


def build_severity_instances(records: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create severity examples only for labels whose polarity is negative."""

    instances = []
    for record in records:
        for label in record.get("labels", []):
            if label["polarity"] != "negative":
                continue
            if label.get("severity") not in SEVERITY_LABELS:
                raise ValueError("Every negative label must have low/medium/high severity")
            instances.append(
                {
                    "review_id": record["review_id"],
                    "text": record["text"],
                    "aspect": label["aspect"],
                    "conditioned_text": f"[ASPECT] {label['aspect']} [REVIEW] {record['text']}",
                    "label": SEVERITY_LABELS.index(label["severity"]),
                }
            )
    return instances


def severity_support_gate(
    train_instances: Sequence[dict[str, Any]],
    validation_instances: Sequence[dict[str, Any]],
    min_train_per_class: int,
    min_validation_per_class: int,
) -> dict[str, Any]:
    """Return a transparent class-support decision for optional severity training."""

    train = Counter(SEVERITY_LABELS[item["label"]] for item in train_instances)
    validation = Counter(SEVERITY_LABELS[item["label"]] for item in validation_instances)
    deficits = [
        label for label in SEVERITY_LABELS
        if train[label] < min_train_per_class or validation[label] < min_validation_per_class
    ]
    return {
        "supported": not deficits,
        "train_support": {label: train[label] for label in SEVERITY_LABELS},
        "validation_support": {label: validation[label] for label in SEVERITY_LABELS},
        "minimum_train_per_class": min_train_per_class,
        "minimum_validation_per_class": min_validation_per_class,
        "unsupported_classes": deficits,
    }


def multilabel_positive_weights(targets: Sequence[Sequence[float]]) -> list[float]:
    """Compute BCE positive weights as negatives/positives for each aspect."""

    values = np.asarray(targets, dtype=float)
    if values.ndim != 2 or not len(values):
        raise ValueError("Multilabel targets must be a non-empty 2D matrix")
    positives = values.sum(axis=0)
    if np.any(positives == 0):
        raise ValueError("Cannot weight an aspect with zero positive training examples")
    return ((len(values) - positives) / positives).tolist()


def classification_weights(labels: Sequence[int], class_count: int) -> list[float]:
    """Compute balanced CE weights: n / (classes * class support)."""

    counts = Counter(labels)
    if any(counts[index] == 0 for index in range(class_count)):
        raise ValueError("Cannot weight a class with zero training examples")
    return [len(labels) / (class_count * counts[index]) for index in range(class_count)]


def validate_prediction_schema(prediction: dict[str, Any], aspects: Iterable[str] | None = None) -> None:
    """Validate the strict review-prediction contract without optional jsonschema."""

    allowed_top = {"review_id", "destination_id", "model_version", "generated_at", "predictions"}
    required_top = {"review_id", "destination_id", "model_version", "predictions"}
    if set(prediction) - allowed_top or not required_top <= prediction.keys():
        raise ValueError("Prediction has missing or additional top-level properties")
    if any(not isinstance(prediction[key], str) or not prediction[key] for key in required_top - {"predictions"}):
        raise ValueError("Prediction identifiers must be non-empty strings")
    if not isinstance(prediction["predictions"], list):
        raise TypeError("predictions must be an array")
    valid_aspects = set(aspects) if aspects is not None else None
    required = {"aspect", "aspect_probability", "polarity"}
    allowed = required | {"polarity_probability", "severity", "severity_probability"}
    for item in prediction["predictions"]:
        if not isinstance(item, dict) or set(item) - allowed or not required <= item.keys():
            raise ValueError("Invalid aspect prediction properties")
        if valid_aspects is not None and item["aspect"] not in valid_aspects:
            raise ValueError(f"Unknown predicted aspect: {item['aspect']}")
        if item["polarity"] not in POLARITY_LABELS:
            raise ValueError("Invalid polarity")
        for key in ("aspect_probability", "polarity_probability", "severity_probability"):
            value = item.get(key)
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1):
                raise ValueError(f"{key} must be a probability or null")
        severity = item.get("severity")
        if severity not in (*SEVERITY_LABELS, None):
            raise ValueError("Invalid severity")
        if item["polarity"] != "negative" and severity is not None:
            raise ValueError("Severity is allowed only for negative polarity")


def _macro_f1(task: str):
    def compute(eval_prediction: Any) -> dict[str, float]:
        logits, labels = eval_prediction
        if task == "aspect":
            predicted = (1 / (1 + np.exp(-logits)) >= 0.5).astype(int)
            score = f1_score(labels, predicted, average="macro", zero_division=0)
        else:
            score = f1_score(labels, np.argmax(logits, axis=-1), average="macro", zero_division=0)
        return {"macro_f1": float(score)}
    return compute


def _plot_logs(log_history: Sequence[dict[str, Any]], output: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    train = [(row["epoch"], row["loss"]) for row in log_history if "loss" in row and "epoch" in row]
    validation = [(row["epoch"], row["eval_loss"]) for row in log_history if "eval_loss" in row and "epoch" in row]
    scores = [(row["epoch"], row["eval_macro_f1"]) for row in log_history if "eval_macro_f1" in row and "epoch" in row]
    fig, left = plt.subplots(figsize=(8, 5))
    if train:
        left.plot(*zip(*train), label="train loss")
    if validation:
        left.plot(*zip(*validation), label="validation loss")
    left.set_xlabel("epoch")
    left.set_ylabel("loss")
    right = left.twinx()
    if scores:
        right.plot(*zip(*scores), color="#1BAF7A", label="validation macro F1")
    right.set_ylim(0, 1)
    right.set_ylabel("macro F1")
    left.set_title(title, loc="left", fontweight="bold")
    left.legend(loc="upper left", frameon=False)
    if scores:
        right.legend(loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _train_task(
    *, task: str, train_rows: Sequence[dict[str, Any]], validation_rows: Sequence[dict[str, Any]],
    labels: Sequence[str], weights: Sequence[float], config: dict[str, Any], output_dir: Path,
) -> dict[str, Any]:
    """Train one task with Hugging Face Trainer; imports stay lazy."""

    try:
        import torch
    except ImportError as error:
        raise RuntimeError(
            "A7 training dependencies are not installed. Use requirements-colab.lock.txt "
            "in a Google Colab GPU runtime."
        ) from error
    from torch.nn import BCEWithLogitsLoss, CrossEntropyLoss
    from transformers import (
        BertForSequenceClassification,
        BertTokenizer,
        DataCollatorWithPadding,
        EarlyStoppingCallback,
        Trainer,
        TrainingArguments,
        set_seed,
    )

    set_seed(config["seed"])
    section = config["indobert"]
    tokenizer = BertTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    model = BertForSequenceClassification.from_pretrained(
        MODEL_ID, revision=MODEL_REVISION, num_labels=len(labels),
        problem_type="multi_label_classification" if task == "aspect" else "single_label_classification",
        id2label={i: label for i, label in enumerate(labels)},
        label2id={label: i for i, label in enumerate(labels)},
    )

    class EncodedDataset(torch.utils.data.Dataset):
        def __init__(self, rows: Sequence[dict[str, Any]]) -> None:
            texts = [row["text"] if task == "aspect" else row["conditioned_text"] for row in rows]
            self.encodings = tokenizer(texts, truncation=True, max_length=section["max_length"])
            self.labels = [row["labels"] if task == "aspect" else row["label"] for row in rows]

        def __len__(self) -> int:
            return len(self.labels)

        def __getitem__(self, index: int) -> dict[str, Any]:
            item = {key: torch.tensor(value[index]) for key, value in self.encodings.items()}
            item["labels"] = torch.tensor(self.labels[index], dtype=torch.float if task == "aspect" else torch.long)
            return item

    loss_weights = torch.tensor(weights, dtype=torch.float)

    class WeightedTrainer(Trainer):
        def compute_loss(self, model: Any, inputs: dict[str, Any], return_outputs: bool = False, num_items_in_batch: Any = None) -> Any:
            target = inputs.pop("labels")
            outputs = model(**inputs)
            current_weights = loss_weights.to(outputs.logits.device)
            loss = (BCEWithLogitsLoss(pos_weight=current_weights)(outputs.logits, target)
                    if task == "aspect" else CrossEntropyLoss(weight=current_weights)(outputs.logits, target))
            return (loss, outputs) if return_outputs else loss

    output_dir.mkdir(parents=True, exist_ok=False)
    precision = section["mixed_precision"]
    arguments = TrainingArguments(
        output_dir=str(output_dir / "checkpoints"), learning_rate=section["learning_rate"],
        per_device_train_batch_size=section["batch_size"], per_device_eval_batch_size=section["batch_size"],
        gradient_accumulation_steps=section["gradient_accumulation_steps"], num_train_epochs=section["epochs"],
        weight_decay=section["weight_decay"], warmup_ratio=section["warmup_ratio"],
        eval_strategy="epoch", save_strategy="epoch", logging_strategy="epoch",
        load_best_model_at_end=True, metric_for_best_model="macro_f1", greater_is_better=True,
        save_total_limit=2, fp16=precision == "fp16", bf16=precision == "bf16",
        seed=config["seed"], data_seed=config["seed"], report_to="none",
    )
    trainer = WeightedTrainer(
        model=model, args=arguments, train_dataset=EncodedDataset(train_rows),
        eval_dataset=EncodedDataset(validation_rows), compute_metrics=_macro_f1(task),
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        callbacks=[EarlyStoppingCallback(early_stopping_patience=section["early_stopping_patience"])],
    )
    result = trainer.train()
    model_dir = output_dir / "model"
    trainer.save_model(model_dir)
    tokenizer.save_pretrained(model_dir)
    metrics = trainer.evaluate()
    logs = trainer.state.log_history
    (output_dir / "trainer-log.json").write_text(json.dumps(logs, indent=2) + "\n", encoding="utf-8")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _plot_logs(logs, output_dir / "training-history.png", f"IndoBERT {task.title()} Training")
    return {"task": task, "best_checkpoint": trainer.state.best_model_checkpoint, "best_metric": trainer.state.best_metric,
            "train_runtime": result.metrics.get("train_runtime"), "metrics": metrics, "model_dir": str(model_dir)}


def offline_reload_smoke_test(model_dir: Path, task: str) -> dict[str, Any]:
    """Reload a saved task fully offline and run one local forward pass."""

    import torch
    from transformers import BertForSequenceClassification, BertTokenizer

    tokenizer = BertTokenizer.from_pretrained(model_dir, local_files_only=True)
    model = BertForSequenceClassification.from_pretrained(model_dir, local_files_only=True)
    model.eval()
    text = "[ASPECT] access [REVIEW] Jalan menuju lokasi rusak." if task != "aspect" else "Jalan menuju lokasi rusak."
    with torch.no_grad():
        logits = model(**tokenizer(text, return_tensors="pt", truncation=True)).logits
    return {"passed": tuple(logits.shape) == (1, model.config.num_labels), "shape": list(logits.shape), "local_files_only": True}


def _artifact_hashes(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "manifest.json"
    }


def _token_coverage_report(
    records: dict[str, list[dict[str, Any]]], max_length: int
) -> dict[str, Any]:
    """Load the pinned tokenizer and report untruncated train/validation token lengths."""

    from transformers import BertTokenizer

    tokenizer = BertTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
    report = {}
    for split in TRAINING_SPLITS:
        encoded = tokenizer(
            [row["text"] for row in records[split]],
            add_special_tokens=True,
            truncation=False,
        )
        report[split] = token_length_summary(
            [len(input_ids) for input_ids in encoded["input_ids"]], max_length
        )
    return report


def run_indobert_training(split_dir: Path, artifact_dir: Path, run_id: str | None = None) -> dict[str, Any]:
    """Run A7 on train/validation only. Intended for a Colab GPU runtime."""

    try:
        import torch
    except ImportError as error:
        raise RuntimeError(
            "A7 training dependencies are not installed. Use requirements-colab.lock.txt "
            "in a Google Colab GPU runtime."
        ) from error

    if not torch.cuda.is_available():
        raise RuntimeError(
            "A7 training requires a CUDA GPU. Run this command in Google Colab with a GPU runtime."
        )
    config = load_config("training")
    section = validate_indobert_config(config)
    taxonomy = load_config("taxonomy")
    aspects = sorted(taxonomy["aspect_definitions"])
    manifest_path = split_dir / "split_manifest_silver_v1.json"
    records, split_manifest, input_hashes = load_training_records(split_dir, manifest_path)
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M_indobert-silver-v1")
    run_dir = artifact_dir / "runs" / run_id
    if run_dir.exists():
        raise FileExistsError(f"Run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)
    random.seed(config["seed"])
    np.random.seed(config["seed"])

    aspect_rows = {
        split: [{"text": row["text"], "labels": target} for row, target in zip(records[split], build_aspect_targets(records[split], aspects))]
        for split in TRAINING_SPLITS
    }
    polarity_rows = {split: build_polarity_instances(records[split]) for split in TRAINING_SPLITS}
    severity_rows = {split: build_severity_instances(records[split]) for split in TRAINING_SPLITS}
    token_coverage = _token_coverage_report(records, section["max_length"])
    (run_dir / "token-length-coverage.json").write_text(
        json.dumps(token_coverage, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    gate = severity_support_gate(
        severity_rows["train"], severity_rows["validation"],
        section["severity_min_train_per_class"], section["severity_min_validation_per_class"],
    )
    results = {
        "aspect": _train_task(task="aspect", train_rows=aspect_rows["train"], validation_rows=aspect_rows["validation"],
                              labels=aspects, weights=multilabel_positive_weights([row["labels"] for row in aspect_rows["train"]]),
                              config=config, output_dir=run_dir / "aspect"),
        "polarity": _train_task(task="polarity", train_rows=polarity_rows["train"], validation_rows=polarity_rows["validation"],
                                labels=POLARITY_LABELS, weights=classification_weights([row["label"] for row in polarity_rows["train"]], 3),
                                config=config, output_dir=run_dir / "polarity"),
    }
    if gate["supported"]:
        results["severity"] = _train_task(task="severity", train_rows=severity_rows["train"], validation_rows=severity_rows["validation"],
                                          labels=SEVERITY_LABELS, weights=classification_weights([row["label"] for row in severity_rows["train"]], 3),
                                          config=config, output_dir=run_dir / "severity")
    else:
        results["severity"] = {"status": "skipped_insufficient_support", "gate": gate}
    smoke = {task: offline_reload_smoke_test(Path(result["model_dir"]), task) for task, result in results.items() if "model_dir" in result}
    (run_dir / "environment.json").write_text(json.dumps(build_environment_snapshot(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {"run_id": run_id, "status": "trained_train_validation_only", "test_read": False,
                "reference_label_type": config["reference_label_type"], "split_version": split_manifest["split_version"],
                "input_hashes": input_hashes, "token_length_coverage": token_coverage,
                "severity_gate": gate, "tasks": results, "offline_reload_smoke": smoke}
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    provenance = {"created_at": datetime.now(timezone.utc).isoformat(), "model": {"id": MODEL_ID, "revision": MODEL_REVISION,
                  "license": MODEL_LICENSE, "parameters": MODEL_PARAMETERS, "tokenizer": TOKENIZER_DESCRIPTION},
                  "training_config_sha256": sha256_file(ML_ROOT / "configs" / "training.yaml"),
                  "taxonomy_sha256": sha256_file(ML_ROOT / "configs" / "taxonomy.yaml"),
                  "split_manifest_sha256": sha256_file(manifest_path), "input_hashes": input_hashes,
                  "test_prohibition": "A7 did not read test; test evaluation is reserved for A8."}
    (run_dir / "manifest.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    provenance["artifact_hashes"] = _artifact_hashes(run_dir)
    (run_dir / "manifest.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary

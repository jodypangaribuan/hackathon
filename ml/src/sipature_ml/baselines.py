"""Keyword and TF-IDF baselines evaluated against locked silver references."""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import matplotlib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    hamming_loss,
    precision_recall_fscore_support,
    precision_score,
    recall_score,
)
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import FeatureUnion

from .config import ML_ROOT, load_config
from .manifest import sha256_file

matplotlib.use("Agg")
import matplotlib.pyplot as plt

NEGATIVE_CUES = (
    "tidak", "gak", "nggak", "buruk", "jelek", "kotor", "rusak", "mahal",
    "bahaya", "berbahaya", "kasar", "lambat", "bau", "pungli", "rawan",
)
POSITIVE_CUES = (
    "bagus", "baik", "bersih", "indah", "nyaman", "aman", "ramah", "murah",
    "terawat", "sejuk", "responsif",
)
HIGH_CUES = ("parah", "sangat berbahaya", "tidak bisa dipakai", "pungli", "preman")
MEDIUM_CUES = ("sangat", "banyak", "terlalu", "rusak", "kotor", "mahal", "buruk")
CONTRASTS = ("tetapi", "tapi", "namun", "walaupun", "meskipun")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _contains(text: str, term: str) -> bool:
    return bool(re.search(rf"(?<!\w){re.escape(term.casefold())}(?!\w)", text.casefold()))


def predict_keyword_labels(text: str, taxonomy: dict[str, Any]) -> list[dict[str, Any]]:
    """Apply an independently specified transparent lexical baseline."""

    lowered = text.casefold()
    labels: list[dict[str, Any]] = []
    for aspect, definition in taxonomy["aspect_definitions"].items():
        terms = [term for term in definition["seed_terms"] if _contains(lowered, term)]
        if not terms:
            continue
        positions = [lowered.find(term.casefold()) for term in terms]
        position = min(item for item in positions if item >= 0)
        start, end = max(0, position - 70), min(len(text), position + 120)
        context = text[start:end]
        local = context.casefold()
        negative = sum(_contains(local, cue) for cue in NEGATIVE_CUES)
        positive = sum(_contains(local, cue) for cue in POSITIVE_CUES)
        # A contrast marker favors cues in the clause containing the aspect mention.
        for marker in CONTRASTS:
            if marker in local:
                clauses = re.split(rf"\b{re.escape(marker)}\b", local, maxsplit=1)
                local = next((clause for clause in clauses if any(term in clause for term in terms)), local)
                negative = sum(_contains(local, cue) for cue in NEGATIVE_CUES)
                positive = sum(_contains(local, cue) for cue in POSITIVE_CUES)
                break
        if negative > positive:
            polarity = "negative"
        elif positive > negative:
            polarity = "positive"
        else:
            polarity = "neutral"
        severity = None
        if polarity == "negative":
            if any(_contains(local, cue) for cue in HIGH_CUES):
                severity = "high"
            elif any(_contains(local, cue) for cue in MEDIUM_CUES):
                severity = "medium"
            else:
                severity = "low"
        labels.append(
            {
                "aspect": aspect,
                "polarity": polarity,
                "severity": severity,
                "matched_terms": terms,
            }
        )
    return labels


def _targets(records: list[dict[str, Any]], aspects: list[str]) -> np.ndarray:
    aspect_index = {aspect: index for index, aspect in enumerate(aspects)}
    target = np.zeros((len(records), len(aspects)), dtype=int)
    for row_index, record in enumerate(records):
        for label in record["labels"]:
            target[row_index, aspect_index[label["aspect"]]] = 1
    return target


def _metric_bundle(
    truth: np.ndarray,
    predicted: np.ndarray,
    aspects: list[str],
    latency_ms_per_review: float,
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    precision, recall, f1, support = precision_recall_fscore_support(
        truth, predicted, average=None, zero_division=0
    )
    result = {
        "reference_label_type": "ai_assisted_weak_supervision_silver",
        "records": len(records),
        "macro_f1": float(f1_score(truth, predicted, average="macro", zero_division=0)),
        "micro_f1": float(f1_score(truth, predicted, average="micro", zero_division=0)),
        "macro_precision": float(
            precision_score(truth, predicted, average="macro", zero_division=0)
        ),
        "macro_recall": float(recall_score(truth, predicted, average="macro", zero_division=0)),
        "exact_match": float(accuracy_score(truth, predicted)),
        "hamming_loss": float(hamming_loss(truth, predicted)),
        "latency_ms_per_review": latency_ms_per_review,
        "per_aspect": {
            aspect: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(f1[index]),
                "support": int(support[index]),
            }
            for index, aspect in enumerate(aspects)
        },
        "by_silver_status": {},
    }
    statuses = sorted({record["silver_status"] for record in records})
    for status in statuses:
        indices = [index for index, record in enumerate(records) if record["silver_status"] == status]
        result["by_silver_status"][status] = {
            "records": len(indices),
            "macro_f1": float(
                f1_score(truth[indices], predicted[indices], average="macro", zero_division=0)
            ),
            "micro_f1": float(
                f1_score(truth[indices], predicted[indices], average="micro", zero_division=0)
            ),
        }
    return result


def evaluate_keyword(
    records: list[dict[str, Any]], aspects: list[str], taxonomy: dict[str, Any]
) -> tuple[dict[str, Any], np.ndarray, list[list[dict[str, Any]]]]:
    start = time.perf_counter()
    labels = [predict_keyword_labels(record["text"], taxonomy) for record in records]
    elapsed = time.perf_counter() - start
    aspect_index = {aspect: index for index, aspect in enumerate(aspects)}
    predicted = np.zeros((len(records), len(aspects)), dtype=int)
    for row_index, row_labels in enumerate(labels):
        for label in row_labels:
            predicted[row_index, aspect_index[label["aspect"]]] = 1
    metrics = _metric_bundle(
        _targets(records, aspects), predicted, aspects, elapsed * 1000 / len(records), records
    )
    return metrics, predicted, labels


def _vectorizer(representation: str, config: dict[str, Any]) -> Any:
    word = TfidfVectorizer(
        ngram_range=tuple(config["word_ngram_range"]),
        min_df=config["min_df"],
        max_features=config["max_features_word"],
        sublinear_tf=True,
    )
    char = TfidfVectorizer(
        analyzer=config["char_analyzer"],
        ngram_range=tuple(config["char_ngram_range"]),
        min_df=config["min_df"],
        max_features=config["max_features_char"],
        sublinear_tf=True,
    )
    if representation == "word":
        return word
    if representation == "char":
        return char
    return FeatureUnion([("word", word), ("char", char)])


def _tune_thresholds(
    truth: np.ndarray, probabilities: np.ndarray, candidates: list[float]
) -> np.ndarray:
    thresholds = np.full(truth.shape[1], 0.5)
    for index in range(truth.shape[1]):
        scored = [
            (
                f1_score(truth[:, index], probabilities[:, index] >= value, zero_division=0),
                -abs(value - 0.5),
                -value,
                value,
            )
            for value in candidates
        ]
        thresholds[index] = max(scored)[-1]
    return thresholds


def train_tfidf(
    train_records: list[dict[str, Any]],
    validation_records: list[dict[str, Any]],
    aspects: list[str],
    config: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Select representation and thresholds using train/validation only."""

    train_text = [record["text"] for record in train_records]
    validation_text = [record["text"] for record in validation_records]
    train_y = _targets(train_records, aspects)
    validation_y = _targets(validation_records, aspects)
    candidates: list[dict[str, Any]] = []
    for representation in config["baselines"]["tfidf"]["representations"]:
        for c_value in config["baselines"]["tfidf"]["c_values"]:
            vectorizer = _vectorizer(representation, config["baselines"]["tfidf"])
            train_x = vectorizer.fit_transform(train_text)
            validation_x = vectorizer.transform(validation_text)
            model = OneVsRestClassifier(
                LogisticRegression(
                    C=c_value,
                    class_weight=config["baselines"]["tfidf"]["class_weight"],
                    max_iter=config["baselines"]["tfidf"]["max_iter"],
                    random_state=config["seed"],
                    solver="liblinear",
                )
            )
            model.fit(train_x, train_y)
            probabilities = model.predict_proba(validation_x)
            thresholds = _tune_thresholds(
                validation_y, probabilities, config["thresholds"]["candidates"]
            )
            predicted = probabilities >= thresholds
            metrics = _metric_bundle(
                validation_y, predicted, aspects, 0.0, validation_records
            )
            candidates.append(
                {
                    "representation": representation,
                    "c": c_value,
                    "vectorizer": vectorizer,
                    "model": model,
                    "thresholds": thresholds,
                    "validation_metrics": metrics,
                }
            )
    best = max(
        candidates,
        key=lambda item: (
            item["validation_metrics"]["macro_f1"],
            item["validation_metrics"]["micro_f1"],
            -config["baselines"]["tfidf"]["representations"].index(item["representation"]),
        ),
    )
    selection = {
        "selected_representation": best["representation"],
        "selected_c": best["c"],
        "thresholds": {aspect: float(best["thresholds"][i]) for i, aspect in enumerate(aspects)},
        "validation_candidates": [
            {
                "representation": item["representation"],
                "c": item["c"],
                "macro_f1": item["validation_metrics"]["macro_f1"],
                "micro_f1": item["validation_metrics"]["micro_f1"],
            }
            for item in candidates
        ],
        "validation_metrics": best["validation_metrics"],
    }
    return best, selection


def evaluate_tfidf(
    fitted: dict[str, Any], records: list[dict[str, Any]], aspects: list[str]
) -> tuple[dict[str, Any], np.ndarray]:
    start = time.perf_counter()
    matrix = fitted["vectorizer"].transform([record["text"] for record in records])
    probabilities = fitted["model"].predict_proba(matrix)
    predicted = probabilities >= fitted["thresholds"]
    elapsed = time.perf_counter() - start
    metrics = _metric_bundle(
        _targets(records, aspects), predicted, aspects, elapsed * 1000 / len(records), records
    )
    return metrics, predicted


def _write_errors(
    path: Path,
    records: list[dict[str, Any]],
    aspects: list[str],
    truth: np.ndarray,
    keyword: np.ndarray,
    tfidf: np.ndarray,
) -> None:
    rows = []
    for row_index, record in enumerate(records):
        for aspect_index, aspect in enumerate(aspects):
            if truth[row_index, aspect_index] != keyword[row_index, aspect_index] or truth[
                row_index, aspect_index
            ] != tfidf[row_index, aspect_index]:
                rows.append(
                    {
                        "review_id": record["review_id"],
                        "destination_id": record["destination_id"],
                        "aspect": aspect,
                        "silver": int(truth[row_index, aspect_index]),
                        "keyword": int(keyword[row_index, aspect_index]),
                        "tfidf": int(tfidf[row_index, aspect_index]),
                        "silver_status": record["silver_status"],
                        "pass_agreement": record["pass_agreement"],
                    }
                )
    pd.DataFrame(rows).to_csv(path, index=False)


def generate_baseline_figures(
    keyword: dict[str, Any],
    tfidf: dict[str, Any],
    selection: dict[str, Any],
    figure_dir: Path,
) -> list[str]:
    figure_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[str] = []
    colors = ["#EB6834", "#2A78D6"]
    fig, ax = plt.subplots(figsize=(8, 5))
    metrics = ["macro_f1", "micro_f1", "exact_match"]
    x = np.arange(len(metrics))
    for offset, (name, result) in enumerate((("Keyword", keyword), ("TF-IDF", tfidf))):
        ax.bar(x + (offset - 0.5) * 0.34, [result[item] for item in metrics], 0.34, label=name, color=colors[offset])
    ax.set_xticks(x, [item.replace("_", " ").title() for item in metrics])
    ax.set_ylim(0, 1)
    ax.set_title("Baseline Agreement terhadap Silver Test", loc="left", fontweight="bold")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    path = figure_dir / "34_baseline_silver_test_comparison.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    outputs.append(path.name)

    aspects = list(keyword["per_aspect"])
    fig, ax = plt.subplots(figsize=(10, 7))
    y = np.arange(len(aspects))
    ax.barh(y + 0.18, [keyword["per_aspect"][a]["f1"] for a in aspects], 0.36, label="Keyword", color=colors[0])
    ax.barh(y - 0.18, [tfidf["per_aspect"][a]["f1"] for a in aspects], 0.36, label="TF-IDF", color=colors[1])
    ax.set_yticks(y, aspects)
    ax.set_xlim(0, 1)
    ax.set_title("Per-Aspect F1 pada Silver Test", loc="left", fontweight="bold")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    path = figure_dir / "35_baseline_per_aspect_f1.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    outputs.append(path.name)

    candidates = selection["validation_candidates"]
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar([item["representation"] for item in candidates], [item["macro_f1"] for item in candidates], color="#7C6BC4")
    ax.bar_label(bars, fmt="%.3f", padding=4)
    ax.set_ylim(0, 1)
    ax.set_title("TF-IDF Validation Representation Selection", loc="left", fontweight="bold")
    ax.set_ylabel("Macro F1 terhadap silver validation")
    ax.spines[["top", "right"]].set_visible(False)
    path = figure_dir / "36_tfidf_validation_selection.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    outputs.append(path.name)
    return outputs


def run_baselines(
    split_dir: Path,
    artifact_dir: Path,
    figure_dir: Path,
) -> dict[str, Any]:
    """Train on train, select on validation, then evaluate the locked test once."""

    config = load_config("training")
    taxonomy = load_config("taxonomy")
    aspects = sorted(taxonomy["aspect_definitions"])
    metrics_dir = artifact_dir / "metrics"
    metric_paths = {
        "keyword": metrics_dir / "keyword-silver-v1-test-metrics.json",
        "tfidf": metrics_dir / "tfidf-silver-v1-test-metrics.json",
    }
    for path in metric_paths.values():
        if path.exists():
            raise FileExistsError(f"Locked-test metric already exists: {path}")
    manifest_path = split_dir / "split_manifest_silver_v1.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not manifest.get("test_is_locked"):
        raise ValueError("Refusing baseline evaluation without a locked test manifest")
    split_records = {
        split: _read_jsonl(split_dir / f"{split}_silver_v1.jsonl")
        for split in ("train", "validation", "test")
    }
    for split, output in manifest["outputs"].items():
        if sha256_file(split_dir / output["path"]) != output["sha256"]:
            raise ValueError(f"Locked split hash mismatch: {split}")

    keyword_validation, _, _ = evaluate_keyword(split_records["validation"], aspects, taxonomy)
    fitted, selection = train_tfidf(
        split_records["train"], split_records["validation"], aspects, config
    )
    keyword_test, keyword_predictions, _ = evaluate_keyword(
        split_records["test"], aspects, taxonomy
    )
    tfidf_test, tfidf_predictions = evaluate_tfidf(fitted, split_records["test"], aspects)

    models_dir = artifact_dir / "models"
    reports_dir = artifact_dir / "reports"
    for path in (metrics_dir, models_dir, reports_dir):
        path.mkdir(parents=True, exist_ok=True)
    keyword_test["model_version"] = "keyword-silver-v1"
    tfidf_test["model_version"] = "tfidf-aspect-silver-v1"
    keyword_test["validation_metrics"] = keyword_validation
    tfidf_test["selection"] = selection
    for name, metrics in (("keyword", keyword_test), ("tfidf", tfidf_test)):
        metric_paths[name].write_text(
            json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    tfidf_model_dir = models_dir / "tfidf-aspect-silver-v1"
    keyword_model_dir = models_dir / "keyword-silver-v1"
    tfidf_model_dir.mkdir(parents=True, exist_ok=True)
    keyword_model_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "vectorizer": fitted["vectorizer"],
            "model": fitted["model"],
            "thresholds": fitted["thresholds"],
            "aspects": aspects,
        },
        tfidf_model_dir / "model.joblib",
    )
    common_manifest = {
        "experiment_version": config["experiment_version"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "split_version": manifest["split_version"],
        "split_manifest_sha256": sha256_file(manifest_path),
        "training_config_sha256": sha256_file(ML_ROOT / "configs" / "training.yaml"),
        "taxonomy_sha256": sha256_file(ML_ROOT / "configs" / "taxonomy.yaml"),
        "reference_label_type": "ai_assisted_weak_supervision_silver",
        "limitations": [
            "Metrics measure agreement with weak-supervision silver labels, not human-gold performance.",
            "Keyword rules and silver rules share taxonomy vocabulary and may have correlated errors.",
        ],
    }
    (keyword_model_dir / "manifest.json").write_text(
        json.dumps({**common_manifest, "model_version": "keyword-silver-v1", "metrics": metric_paths["keyword"].name}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (tfidf_model_dir / "manifest.json").write_text(
        json.dumps({**common_manifest, "model_version": "tfidf-aspect-silver-v1", "metrics": metric_paths["tfidf"].name, "selection": selection}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_errors(
        reports_dir / "baseline_silver_test_errors.csv",
        split_records["test"],
        aspects,
        _targets(split_records["test"], aspects),
        keyword_predictions,
        tfidf_predictions,
    )
    figures = generate_baseline_figures(keyword_test, tfidf_test, selection, figure_dir)
    summary = {
        "experiment_version": config["experiment_version"],
        "split_version": manifest["split_version"],
        "selected_tfidf_representation": selection["selected_representation"],
        "keyword_test_macro_f1": keyword_test["macro_f1"],
        "tfidf_test_macro_f1": tfidf_test["macro_f1"],
        "keyword_test_micro_f1": keyword_test["micro_f1"],
        "tfidf_test_micro_f1": tfidf_test["micro_f1"],
        "figures": figures,
        "reference_label_type": "ai_assisted_weak_supervision_silver",
    }
    (reports_dir / "baseline_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary

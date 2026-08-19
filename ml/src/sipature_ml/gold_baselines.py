"""Human-gold baseline evaluation (keyword + TF-IDF) reusing the locked split.

The gold annotation by the three team members (`gold.jsonl`, produced via
`annotation-agreement` + `freeze-gold`) is the human-verified reference. This
module evaluates the keyword and TF-IDF baselines against that reference using
the SAME leakage-safe split assignment as the silver baselines: the review ->
split mapping is reused verbatim and only the reference labels change.

This keeps the frozen silver metrics (`*-silver-v1-test-metrics.json`) and the
locked silver test untouched; gold metrics are written separately as
`*-gold-v1-test-metrics.json` with `reference_label_type = "human_gold"`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .baselines import _read_jsonl, evaluate_keyword, evaluate_tfidf, train_tfidf
from .config import load_config
from .manifest import sha256_file

SPLIT_NAMES = ("train", "validation", "test")


def load_gold_labels(gold_path: Path) -> dict[str, list[dict[str, Any]]]:
    """Map review_id -> gold labels, validating the frozen gold artifact."""
    records = _read_jsonl(gold_path)
    labels: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        if record["review_id"] in labels:
            raise ValueError(f"Duplicate gold review_id: {record['review_id']}")
        labels[record["review_id"]] = record["labels"]
    return labels


def build_gold_split_records(
    split_dir: Path, gold_labels: dict[str, list[dict[str, Any]]]
) -> dict[str, list[dict[str, Any]]]:
    """Reuse the locked silver split assignment with gold labels substituted."""
    manifest_path = split_dir / "split_manifest_silver_v1.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not manifest.get("test_is_locked"):
        raise ValueError("Refusing gold evaluation without a locked split manifest")
    for split, output in manifest["outputs"].items():
        if sha256_file(split_dir / output["path"]) != output["sha256"]:
            raise ValueError(f"Locked split hash mismatch: {split}")

    split_records: dict[str, list[dict[str, Any]]] = {}
    for split in SPLIT_NAMES:
        records = _read_jsonl(split_dir / f"{split}_silver_v1.jsonl")
        missing = [record["review_id"] for record in records if record["review_id"] not in gold_labels]
        if missing:
            raise ValueError(f"{split}: {len(missing)} reviews missing from gold")
        for record in records:
            record["labels"] = gold_labels[record["review_id"]]
            record["label_source"] = "human_gold"
        split_records[split] = records
    return split_records


def run_gold_baselines(
    split_dir: Path,
    gold_path: Path,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Evaluate keyword + TF-IDF baselines against human-gold labels."""
    config = load_config("training")
    taxonomy = load_config("taxonomy")
    aspects = sorted(taxonomy["aspect_definitions"])

    gold_labels = load_gold_labels(gold_path)
    split_records = build_gold_split_records(split_dir, gold_labels)
    manifest = json.loads((split_dir / "split_manifest_silver_v1.json").read_text(encoding="utf-8"))

    keyword_validation, _, _ = evaluate_keyword(split_records["validation"], aspects, taxonomy)
    fitted, selection = train_tfidf(
        split_records["train"], split_records["validation"], aspects, config
    )
    keyword_test, _, _ = evaluate_keyword(split_records["test"], aspects, taxonomy)
    tfidf_test, _ = evaluate_tfidf(fitted, split_records["test"], aspects)

    for metrics in (keyword_test, tfidf_test):
        metrics["reference_label_type"] = "human_gold"
    keyword_test["model_version"] = "keyword-gold-v1"
    keyword_test["validation_metrics"] = keyword_validation
    tfidf_test["model_version"] = "tfidf-aspect-gold-v1"
    tfidf_test["selection"] = selection

    metrics_dir = artifact_dir / "metrics"
    reports_dir = artifact_dir / "reports"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    keyword_path = metrics_dir / "keyword-gold-v1-test-metrics.json"
    tfidf_path = metrics_dir / "tfidf-gold-v1-test-metrics.json"
    keyword_path.write_text(
        json.dumps(keyword_test, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    tfidf_path.write_text(
        json.dumps(tfidf_test, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    summary = {
        "reference_label_type": "human_gold",
        "split_version": manifest["split_version"],
        "gold_sha256": sha256_file(gold_path),
        "split_manifest_sha256": sha256_file(split_dir / "split_manifest_silver_v1.json"),
        "selected_tfidf_representation": selection["selected_representation"],
        "keyword_test_macro_f1": keyword_test["macro_f1"],
        "keyword_test_micro_f1": keyword_test["micro_f1"],
        "keyword_test_exact_match": keyword_test["exact_match"],
        "tfidf_test_macro_f1": tfidf_test["macro_f1"],
        "tfidf_test_micro_f1": tfidf_test["micro_f1"],
        "tfidf_test_exact_match": tfidf_test["exact_match"],
        "per_aspect": {
            aspect: {
                "keyword_f1": keyword_test["per_aspect"][aspect]["f1"],
                "tfidf_f1": tfidf_test["per_aspect"][aspect]["f1"],
                "support": keyword_test["per_aspect"][aspect]["support"],
            }
            for aspect in aspects
        },
    }
    (reports_dir / "gold_baseline_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary

import json

import pandas as pd

from sipature_ml.annotation import (
    _annotation_template,
    _consensus_labels,
    _contains_term,
    _language_marker,
    evaluate_agreement,
    freeze_gold,
    label_review_pass,
    validate_annotation_record,
)


def _record(annotator: str, labels: list[dict]) -> dict:
    return {
        "review_id": "r1",
        "destination_id": "d1",
        "text": "Pemandangan indah tetapi toilet kotor.",
        "rating_context": 4,
        "labels": labels,
        "annotator_id": annotator,
        "annotation_version": "1.0.0-rc1",
        "annotation_status": "completed",
        "review_notes": None,
    }


def test_language_marker_detects_mixed_markers() -> None:
    assert _language_marker("tempat good and bagus") == "mixed"


def test_candidate_terms_use_word_boundaries() -> None:
    assert _contains_term("tempat ini aman", ["aman"])
    assert not _contains_term("makanannya enak", ["aman"])
    assert not _contains_term("bukan hari ini", ["buka"])


def test_validation_enforces_severity_constraint() -> None:
    record = _record(
        "A1",
        [{"aspect": "scenery", "polarity": "positive", "severity": "low", "evidence_text": "Pemandangan indah", "notes": None}],
    )
    assert any("severity must be null" in error for error in validate_annotation_record(record))


def test_agreement_metrics_on_identical_annotations(tmp_path) -> None:
    labels = [
        {"aspect": "scenery", "polarity": "positive", "severity": None, "evidence_text": "Pemandangan indah", "notes": None},
        {"aspect": "sanitation", "polarity": "negative", "severity": "medium", "evidence_text": "toilet kotor", "notes": None},
    ]
    paths = []
    for annotator in ("A1", "A2"):
        path = tmp_path / f"{annotator}.jsonl"
        path.write_text(json.dumps(_record(annotator, labels), ensure_ascii=False) + "\n", encoding="utf-8")
        paths.append(path)
    metrics = evaluate_agreement(paths, tmp_path / "metrics.json")
    assert metrics["aspect_jaccard_mean"] == 1.0
    assert metrics["polarity_agreement"] == 1.0


def test_annotation_template_uses_explicit_index_id() -> None:
    row = pd.Series(
        {"destination_id": "d1", "review_text_raw": "Bagus", "rating": 5.0}
    )
    assert _annotation_template("r1", row, "A1")["review_id"] == "r1"


def test_freeze_gold_rejects_missing_adjudication(tmp_path) -> None:
    metrics = {
        "aspect_jaccard_mean": 1.0,
        "polarity_agreement": 1.0,
        "severity_weighted_kappa": 1.0,
        "disagreement_review_ids": ["r1"],
    }
    metrics_path = tmp_path / "metrics.json"
    metrics_path.write_text(json.dumps(metrics), encoding="utf-8")
    annotations = tmp_path / "annotations.jsonl"
    annotations.write_text("", encoding="utf-8")
    adjudicated = tmp_path / "adjudicated.jsonl"
    adjudicated.write_text("", encoding="utf-8")
    try:
        freeze_gold([annotations], adjudicated, metrics_path, tmp_path / "gold.jsonl")
    except ValueError as error:
        assert "Missing adjudication" in str(error)
    else:
        raise AssertionError("freeze_gold must reject missing adjudication")


def test_silver_pass_handles_negated_positive_term() -> None:
    labels = label_review_pass("Tempatnya tidak bersih dan kotor.", "balanced")
    cleanliness = next(label for label in labels if label["aspect"] == "cleanliness")
    assert cleanliness["polarity"] == "negative"
    assert cleanliness["evidence_text"] in "Tempatnya tidak bersih dan kotor."


def test_silver_pass_assigns_high_severity_from_textual_impact() -> None:
    labels = label_review_pass("Toilet tidak bisa dipakai dan tidak ada air.", "balanced")
    sanitation = next(label for label in labels if label["aspect"] == "sanitation")
    assert sanitation["polarity"] == "negative"
    assert sanitation["severity"] == "high"


def test_consensus_requires_two_pass_votes() -> None:
    common = {"aspect": "access", "polarity": "negative", "severity": "medium", "evidence_text": "jalan rusak"}
    labels, _, disagreements = _consensus_labels(
        {"strict": [common], "balanced": [common], "recall": []}
    )
    assert labels[0]["vote_count"] == 2
    assert disagreements[0]["reason"] == "partial_consensus"


def test_silver_price_transparency_handles_no_extortion() -> None:
    labels = label_review_pass("Tempat bersih dan aman dari pungli.", "balanced")
    price = next(label for label in labels if label["aspect"] == "price_transparency")
    assert price["polarity"] == "positive"
    assert price["severity"] is None


def test_silver_boundary_excludes_road_damage_from_maintenance() -> None:
    labels = label_review_pass("Jalan menuju lokasi rusak parah.", "balanced")
    aspects = {label["aspect"] for label in labels}
    assert "access" in aspects
    assert "maintenance" not in aspects


def test_silver_boundary_toilet_is_sanitation_not_general_cleanliness() -> None:
    labels = label_review_pass("Toilet sangat kotor dan bau.", "balanced")
    aspects = {label["aspect"] for label in labels}
    assert "sanitation" in aspects
    assert "cleanliness" not in aspects


def test_silver_handles_colloquial_no_extortion() -> None:
    labels = label_review_pass("View bagus, gadak pungli.", "balanced")
    price = next(label for label in labels if label["aspect"] == "price_transparency")
    assert price["polarity"] == "positive"


def test_silver_extortion_question_is_neutral() -> None:
    labels = label_review_pass("Benarkah tempat ini banyak pungli ya?", "balanced")
    price = next(label for label in labels if label["aspect"] == "price_transparency")
    assert price["polarity"] == "neutral"


def test_no_hot_water_is_not_high_outside_sanitation() -> None:
    labels = label_review_pass("Tidak ada air panas.", "balanced")
    comfort = next(label for label in labels if label["aspect"] == "comfort")
    assert comfort["severity"] != "high"

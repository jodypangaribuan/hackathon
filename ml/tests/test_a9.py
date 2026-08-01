from datetime import date

import pandas as pd
import pytest

from sipature_ml.a9 import (
    aggregate_frames,
    bayesian_rate,
    build_expert_review_queue,
    classify_polarity,
    freshness_weight,
    prioritize_frames,
    priority_score,
    validate_export,
    weight_sensitivity,
)
from sipature_ml.config import load_config


def test_lexical_polarity_is_aspect_conditioned() -> None:
    taxonomy = load_config("taxonomy")
    text = "Pemandangan indah, tetapi parkir sangat buruk dan mahal."
    assert classify_polarity(text, "scenery", taxonomy) == "positive"
    assert classify_polarity(text, "parking", taxonomy) == "negative"


def test_bayesian_rate_and_freshness_are_bounded() -> None:
    assert bayesian_rate(1, 2, 0.2, 10) == pytest.approx(0.25)
    assert freshness_weight("2024-01-01", date(2024, 1, 1), 365) == 1.0
    assert freshness_weight("2023-01-01", date(2024, 1, 1), 365) == pytest.approx(0.5)
    assert freshness_weight(None, date(2024, 1, 1), 365) == 0.5


def test_priority_renormalizes_missing_components() -> None:
    weights = load_config("scoring")["priority_weights"]
    result = priority_score(
        {
            "severity": None,
            "complaint_frequency": 0.8,
            "model_confidence": 0.6,
            "persistence": 1.0,
            "visitor_exposure": 0.4,
            "facility_gap": None,
            "feasibility": None,
        },
        weights,
    )
    assert result["available_weight"] == pytest.approx(0.60)
    assert sum(item["effective_weight"] for item in result["components"].values()) == pytest.approx(1)
    assert 0 <= result["score"] <= 1


def test_aggregation_marks_severity_unavailable_and_deduplicates_evidence() -> None:
    config = load_config("a9")
    predictions = pd.DataFrame([
        {
            "review_id": "r1", "destination_id": "d1", "review_text": "Parkir buruk.",
            "published_date_estimate": "2025-01-01", "duplicate_group_id": "dup1",
            "source_file": "restricted.csv", "source_row": 1,
            "predictions": [{"aspect": "parking", "aspect_probability": 0.9,
                             "polarity": "negative", "polarity_probability": 0.5,
                             "polarity_model_version": "lexical-polarity-v1", "severity": None,
                             "severity_probability": None,
                             "severity_status": "unavailable_no_supported_model"}],
        },
        {
            "review_id": "r2", "destination_id": "d1", "review_text": "Parkir buruk.",
            "published_date_estimate": "2025-01-01", "duplicate_group_id": "dup1",
            "source_file": "restricted.csv", "source_row": 2,
            "predictions": [{"aspect": "parking", "aspect_probability": 0.8,
                             "polarity": "negative", "polarity_probability": 0.5,
                             "polarity_model_version": "lexical-polarity-v1", "severity": None,
                             "severity_probability": None,
                             "severity_status": "unavailable_no_supported_model"}],
        },
    ])
    reviews = pd.DataFrame([
        {"destination_id": "d1", "has_text": True},
        {"destination_id": "d1", "has_text": False},
    ])
    signals, evidence = aggregate_frames(predictions, reviews, config)
    assert signals.iloc[0]["mention_count"] == 2
    assert signals.iloc[0]["complaint_rate"] == 1.0
    assert signals.iloc[0]["severe_count"] is None
    assert signals.iloc[0]["severity_status"] == "unavailable_no_supported_model"
    assert signals.iloc[0]["text_review_count"] == 1
    assert signals.iloc[0]["all_review_count"] == 2
    assert len(evidence) == 1
    assert evidence.iloc[0]["review_id"] == "r1"


def test_export_gate_requires_evidence_for_actionable_issue() -> None:
    payload = {
        "schema_version": "1.0.0", "model_version": "a9", "generated_at": "now",
        "source_manifest": "a" * 64, "limitations": ["silver"],
        "destinations": [{
            "destination_id": "d1", "issues": [{
                "priority": "High", "evidence": [],
                "severity_status": "unavailable_no_supported_model",
                "explanation": "Available components only.",
                "recommended_verification": "Inspect.",
            }],
        }],
    }
    with pytest.raises(ValueError, match="must contain evidence"):
        validate_export(payload)
    payload["destinations"][0]["issues"][0]["priority"] = "Insufficient Data"
    validate_export(payload)


def test_unresolved_destination_never_receives_operational_priority() -> None:
    signals = pd.DataFrame([{
        "destination_id": "d1", "aspect": "parking", "mention_count": 10,
        "negative_count": 8, "severe_count": None, "complaint_rate": 0.8,
        "smoothed_complaint_rate": 0.7, "mean_confidence": 0.9, "persistence": 1.0,
        "freshness": 1.0, "unique_review_count": 10, "text_review_count": 20,
        "all_review_count": 30,
        "data_confidence": "medium", "severity_status": "unavailable_no_supported_model",
    }])
    destinations = pd.DataFrame([{
        "destination_id": "d1", "canonical_name": "Unresolved", "kind": "wisata",
        "latitude": None, "longitude": None, "address": None, "category": None,
        "canonical_status": "unresolved_placeholder",
    }])
    result = prioritize_frames(signals, destinations, load_config("a9"))
    assert result.iloc[0]["priority"] == "Insufficient Data"
    assert result.iloc[0]["issues"][0]["priority"] == "Insufficient Data"


def test_expert_queue_has_empty_human_judgment_fields() -> None:
    prioritized = pd.DataFrame([{
        "destination_id": "d1", "name": "Place", "priority": "High", "priority_score": 0.8,
        "canonical_status": "metadata_anchor", "issues": [{
            "aspect": "parking", "priority": "High", "priority_score": 0.8,
            "priority_components": {"complaint_frequency": {"value": 0.8}},
            "recommended_verification": "Inspect.", "candidate_intervention": "Fix.",
        }],
    }])
    evidence = pd.DataFrame([{"destination_id": "d1", "aspect": "parking", "text": "Quote"}])
    queue = build_expert_review_queue(prioritized, evidence, 25)
    assert len(queue) == 1
    assert queue.iloc[0]["issue_correct"] is None
    assert queue.iloc[0]["evidence"] == ["Quote"]


def test_weight_sensitivity_reports_each_component() -> None:
    weights = load_config("scoring")["priority_weights"]
    components = {
        "complaint_frequency": {"value": 0.8}, "model_confidence": {"value": 0.7},
        "persistence": {"value": 1.0}, "visitor_exposure": {"value": 0.5},
        "feasibility": {"value": 0.5},
    }
    rows = pd.DataFrame([{
        "destination_id": f"d{index}", "priority": "High", "priority_score": 0.8 - index / 100,
        "issues": [{"priority": "High", "priority_components": components}],
    } for index in range(25)])
    result = weight_sensitivity(rows, weights)
    assert len(result["scenarios"]) == len(weights)
    assert all(0 <= item["top20_jaccard"] <= 1 for item in result["scenarios"].values())

import hashlib
import json
from pathlib import Path

import pytest

from sipature_ml.config import load_config
from sipature_ml.indobert import (
    build_aspect_targets,
    build_polarity_instances,
    build_severity_instances,
    classification_weights,
    multilabel_positive_weights,
    severity_support_gate,
    token_length_summary,
    validate_indobert_config,
    validate_prediction_schema,
    verify_training_split_hashes,
)


@pytest.fixture
def records() -> list[dict]:
    return [
        {
            "review_id": "r1",
            "text": "Jalan rusak tetapi pemandangan bagus.",
            "labels": [
                {"aspect": "access", "polarity": "negative", "severity": "high"},
                {"aspect": "scenery", "polarity": "positive", "severity": None},
            ],
        },
        {"review_id": "r2", "text": "Biasa saja.", "labels": []},
    ]


def test_config_pins_model_revision_and_metadata() -> None:
    section = validate_indobert_config(load_config("training"))
    assert section["model_id"] == "indobenchmark/indobert-base-p1"
    assert section["revision"] == "c2cd0b51ddce6580eb35263b39b0a1e5fb0a39e2"
    assert section["license"] == "MIT"
    assert section["parameter_count"] == 124_500_000


def test_hash_verifier_reads_only_train_and_validation(tmp_path: Path) -> None:
    outputs = {}
    for split in ("train", "validation"):
        path = tmp_path / f"{split}.jsonl"
        path.write_text(f'{{"split":"{split}"}}\n', encoding="utf-8")
        outputs[split] = {"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    outputs["test"] = {"path": "must-not-exist.jsonl", "sha256": "invalid"}
    assert set(verify_training_split_hashes(tmp_path, {"outputs": outputs})) == {"train", "validation"}


def test_targets_and_conditioned_instances(records: list[dict]) -> None:
    assert build_aspect_targets(records, ["access", "scenery"]) == [[1.0, 1.0], [0.0, 0.0]]
    polarity = build_polarity_instances(records)
    severity = build_severity_instances(records)
    assert len(polarity) == 2
    assert polarity[0]["conditioned_text"].startswith("[ASPECT] access [REVIEW]")
    assert severity == [{
        "review_id": "r1", "text": records[0]["text"], "aspect": "access",
        "conditioned_text": f"[ASPECT] access [REVIEW] {records[0]['text']}", "label": 2,
    }]


def test_weights_and_severity_gate() -> None:
    assert multilabel_positive_weights([[1, 0], [1, 1], [0, 1]]) == [0.5, 0.5]
    assert classification_weights([0, 0, 1, 2], 3) == pytest.approx([2 / 3, 4 / 3, 4 / 3])
    train = [{"label": label} for label in [0, 0, 1, 1, 2, 2]]
    validation = [{"label": label} for label in [0, 1, 2]]
    assert severity_support_gate(train, validation, 2, 1)["supported"] is True
    gate = severity_support_gate(train, validation, 3, 1)
    assert gate["supported"] is False
    assert gate["unsupported_classes"] == ["low", "medium", "high"]


def test_token_length_summary_reports_configured_coverage() -> None:
    summary = token_length_summary([10, 20, 30, 200], max_length=192)
    assert summary["p50_tokens"] == 20
    assert summary["maximum_tokens"] == 200
    assert summary["records_within_max_length"] == 3
    assert summary["coverage_at_max_length"] == 0.75


def test_prediction_schema_enforces_negative_only_severity() -> None:
    prediction = {
        "review_id": "r1", "destination_id": "d1", "model_version": "v1",
        "predictions": [{
            "aspect": "access", "aspect_probability": 0.9, "polarity": "negative",
            "polarity_probability": 0.8, "severity": "high", "severity_probability": 0.7,
        }],
    }
    validate_prediction_schema(prediction, ["access"])
    invalid = json.loads(json.dumps(prediction))
    invalid["predictions"][0]["polarity"] = "positive"
    with pytest.raises(ValueError, match="Severity is allowed only"):
        validate_prediction_schema(invalid, ["access"])

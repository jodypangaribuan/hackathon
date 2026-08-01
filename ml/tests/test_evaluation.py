import json
from pathlib import Path

import numpy as np
import pytest

from sipature_ml.evaluation import (
    aspect_metrics,
    expected_calibration_error,
    fit_multilabel_temperature,
    multilabel_brier_score,
    multilabel_nll,
    polarity_metrics,
    run_calibration,
    sigmoid,
    softmax,
    tune_alert_thresholds,
    tune_detection_thresholds,
    validate_calibration_contract,
    validate_model_contract,
)
from sipature_ml.manifest import sha256_file


def test_stable_probability_helpers() -> None:
    assert np.allclose(sigmoid(np.array([-1000.0, 0.0, 1000.0])), [0, 0.5, 1])
    assert np.allclose(softmax(np.array([[1000.0, 1001.0]])), [[0.26894142, 0.73105858]])


def test_temperature_nonworsens_nll() -> None:
    logits = np.array([[4.0, -4.0], [2.0, -2.0], [-3.0, 3.0]])
    targets = np.array([[1, 0], [0, 1], [0, 1]])
    result = fit_multilabel_temperature(logits, targets, 0.5, 5.0, 91)
    assert result["nll_after"] <= multilabel_nll(logits, targets)


def test_detection_threshold_tie_chooses_lowest() -> None:
    probabilities = np.array([[0.9], [0.1]])
    targets = np.array([[1], [0]])
    assert tune_detection_thresholds(probabilities, targets, [0.8, 0.5]).tolist() == [0.5]


def test_alert_threshold_requires_support_then_precision_recall_tie() -> None:
    probabilities = np.array([[0.95], [0.9], [0.8], [0.7]])
    targets = np.array([[1], [0], [1], [0]])
    result = tune_alert_thresholds(probabilities, targets, [0.75, 0.85], 2, 0.5)[0]
    assert result["threshold"] == 0.75
    assert result["predicted_support"] == 3
    unavailable = tune_alert_thresholds(probabilities, targets, [0.9], 3, 0.8)[0]
    assert unavailable["threshold"] is None


def test_calibration_scores_metrics_and_polarity() -> None:
    probabilities = np.array([[0.9, 0.2], [0.1, 0.8]])
    targets = np.array([[1, 0], [0, 1]])
    assert expected_calibration_error(probabilities, targets, 5) == pytest.approx(0.15)
    assert multilabel_brier_score(probabilities, targets) == pytest.approx(0.025)
    metrics = aspect_metrics(targets, probabilities, [0.5, 0.5], ["a", "b"], [0.8, 0.8], 0.02)
    assert metrics["macro_f1"] == 1
    assert metrics["micro_f1"] == 1
    assert metrics["precision_at_alert"]["a"]["precision"] == 1
    polarity = polarity_metrics([0, 1, 2], [0, 2, 2])
    assert len(polarity["confusion_matrix"]) == 3
    assert polarity["macro_f1"] < 1


def test_model_and_calibration_hash_contract(tmp_path: Path) -> None:
    hashes = {}
    for relative in ("aspect/model/model.safetensors", "polarity/model/model.safetensors"):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(relative.encode())
        hashes[relative] = sha256_file(path)
    assert validate_model_contract(tmp_path, {"artifact_hashes": hashes}) == hashes
    validate_calibration_contract(
        {"artifact_sha256": "frozen", "model_hashes": hashes}, "frozen", hashes
    )
    with pytest.raises(ValueError, match="model hashes"):
        validate_calibration_contract(
            {"artifact_sha256": "frozen", "model_hashes": {}}, "frozen", hashes
        )


def test_calibration_never_resolves_test_and_refuses_overwrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    split_dir = tmp_path / "splits"
    model_dir = tmp_path / "model"
    split_dir.mkdir()
    validation = split_dir / "validation.jsonl"
    validation.write_text(
        json.dumps({"review_id": "r1", "text": "x", "labels": []}) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "outputs": {
            "validation": {"path": validation.name, "sha256": sha256_file(validation)},
            "test": {"path": "directory-that-must-not-exist/test.jsonl", "sha256": "never"},
        }
    }
    (split_dir / "split_manifest_silver_v1.json").write_text(json.dumps(manifest), encoding="utf-8")
    model_dir.mkdir()
    (model_dir / "manifest.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        "sipature_ml.evaluation._load_a7_contract",
        lambda *_: ({"input_hashes": {"validation": sha256_file(validation)}}, {}),
    )
    monkeypatch.setattr("sipature_ml.evaluation.load_config", lambda name: {
        "training": {
            "indobert": {"model_id": "x", "revision": "x", "max_length": 8},
            "calibration": {"version": "v", "output_version": "v", "temperature_min": 0.5,
                            "temperature_max": 2.0, "temperature_grid_size": 5, "ece_bins": 2,
                            "threshold_candidates": [0.5], "alert_minimum_predictions": 1,
                            "alert_minimum_precision": 0.8},
        },
        "taxonomy": {"aspect_definitions": {"access": {}}},
    }[name])
    output = tmp_path / "calibration"
    result = run_calibration(
        split_dir, model_dir, output,
        inference_fn=lambda *_: {"aspect_logits": np.array([[0.0]]),
                                 "polarity_logits": np.empty((0, 3)), "latency_seconds": 0},
    )
    assert result["test_read"] is False
    assert not (split_dir / "directory-that-must-not-exist").exists()
    with pytest.raises(FileExistsError):
        run_calibration(split_dir, model_dir, output)

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
    run_locked_test_evaluation,
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
    metrics = aspect_metrics(
        targets, probabilities, [0.5, 0.5], ["a", "b"], [0.8, 0.8],
        {"a": {"target_met": True}, "b": {"target_met": True}}, 0.02,
    )
    assert metrics["macro_f1"] == 1
    assert metrics["micro_f1"] == 1
    assert metrics["precision_at_alert"]["per_label"]["a"]["precision"] == 1
    assert metrics["precision_at_alert"]["overall_micro"]["predicted_support"] == 2
    polarity = polarity_metrics([0, 1, 2], [0, 2, 2])
    assert len(polarity["confusion_matrix"]) == 3
    assert polarity["macro_f1"] < 1


def test_model_and_calibration_hash_contract(tmp_path: Path) -> None:
    hashes = {}
    filenames = (
        "config.json", "model.safetensors", "special_tokens_map.json",
        "tokenizer_config.json", "vocab.txt",
    )
    for relative in (
        f"{task}/model/{filename}" for task in ("aspect", "polarity") for filename in filenames
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(relative.encode())
        hashes[relative] = sha256_file(path)
    assert validate_model_contract(tmp_path, {"artifact_hashes": hashes}) == hashes
    contract = {
        "phase": "validation_calibration", "test_read": False, "model_hashes": hashes,
        "split_manifest_sha256": "split", "validation_sha256": "validation",
        "labels": ["a"], "calibration_config_canonical_sha256": "calibration-config",
        "indobert_config_canonical_sha256": "indobert-config", "temperature": 1.0,
        "detection_thresholds": {"a": 0.5}, "alert_thresholds": {"a": 0.8},
        "alert_validation": {"a": {"target_met": True}},
    }
    manifest = {
        "phase": "validation_calibration", "test_read": False,
        "calibration_sha256": "frozen",
    }
    validate_calibration_contract(
        contract, "frozen", manifest, hashes, "split", "validation", ["a"],
        "calibration-config", "indobert-config",
    )
    with pytest.raises(ValueError, match="model hashes"):
        validate_calibration_contract(
            {**contract, "model_hashes": {}}, "frozen", manifest, hashes, "split",
            "validation", ["a"], "calibration-config", "indobert-config",
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
                            "alert_minimum_precision": 0.8, "inference_batch_size": 2,
                            "require_cuda": False},
        },
        "taxonomy": {"aspect_definitions": {"access": {}}},
    }[name])
    output = tmp_path / "calibration"
    result = run_calibration(
        split_dir, model_dir, output,
        inference_fn=lambda *_: {"aspect_logits": np.array([[0.0]]),
                                 "polarity_logits": np.empty((0, 3)),
                                 "aspect_latency_seconds": 0, "polarity_latency_seconds": 0},
    )
    assert result["test_read"] is False
    assert not (split_dir / "directory-that-must-not-exist").exists()
    with pytest.raises(FileExistsError):
        run_calibration(split_dir, model_dir, output)


def _write_calibration_fixture(
    tmp_path: Path, split_hash: str, validation_hash: str, labels: list[str], model_hashes: dict[str, str],
) -> Path:
    directory = tmp_path / "calibration"
    directory.mkdir()
    calibration = {
        "phase": "validation_calibration", "test_read": False, "labels": labels,
        "temperature": 1.0, "detection_thresholds": {label: 0.5 for label in labels},
        "alert_thresholds": {label: 0.8 for label in labels},
        "alert_validation": {label: {"target_met": True} for label in labels},
        "validation_sha256": validation_hash, "split_manifest_sha256": split_hash,
        "a7_manifest_sha256": "a7", "calibration_config_canonical_sha256": "cc",
        "indobert_config_canonical_sha256": "ic", "model_hashes": model_hashes,
    }
    calibration_path = directory / "calibration.json"
    calibration_path.write_text(json.dumps(calibration), encoding="utf-8")
    (directory / "validation-predictions.npz").write_bytes(b"predictions")
    (directory / "calibration.png").write_bytes(b"plot")
    artifacts = {
        path.name: sha256_file(path) for path in (
            calibration_path, directory / "validation-predictions.npz", directory / "calibration.png"
        )
    }
    (directory / "manifest.json").write_text(json.dumps({
        "phase": "validation_calibration", "test_read": False,
        "calibration_sha256": sha256_file(calibration_path), "artifact_hashes": artifacts,
    }), encoding="utf-8")
    return directory


def test_locked_evaluation_preflight_before_test_access_and_tamper(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    split_dir = tmp_path / "splits"
    split_dir.mkdir()
    manifest_path = split_dir / "split_manifest_silver_v1.json"
    manifest = {"test_is_locked": True, "outputs": {"validation": {"sha256": "validation"}},
                "reference_label_type": "silver", "split_version": "v"}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    calibration_dir = _write_calibration_fixture(
        tmp_path, "wrong-split", "validation", ["a"], {},
    )
    monkeypatch.setattr("sipature_ml.evaluation._load_a7_contract", lambda *_: ({}, {}))
    monkeypatch.setattr("sipature_ml.evaluation.load_config", lambda name: {
        "training": {"indobert": {}, "calibration": {}},
        "taxonomy": {"aspect_definitions": {"a": {}}},
    }[name])
    with pytest.raises(ValueError, match="split manifest"):
        run_locked_test_evaluation(split_dir, tmp_path, calibration_dir, tmp_path / "evaluation")
    assert not (tmp_path / "evaluation").exists()

    calibration_dir.joinpath("calibration.png").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="artifact hash mismatch"):
        run_locked_test_evaluation(split_dir, tmp_path, calibration_dir, tmp_path / "evaluation")


def test_locked_evaluation_claim_marker_one_inference_and_overwrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    split_dir = tmp_path / "synthetic-splits"
    split_dir.mkdir()
    test_path = split_dir / "synthetic-test.jsonl"
    test_path.write_text(json.dumps({"review_id": "r1", "text": "x", "labels": []}) + "\n")
    manifest_path = split_dir / "split_manifest_silver_v1.json"
    manifest = {
        "test_is_locked": True, "outputs": {
            "validation": {"sha256": "validation"},
            "test": {"path": test_path.name, "sha256": sha256_file(test_path)},
        }, "reference_label_type": "silver", "split_version": "v",
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    (model_dir / "manifest.json").write_text("a7")
    calibration_dir = _write_calibration_fixture(
        tmp_path, sha256_file(manifest_path), "validation", ["a"], {},
    )
    calibration_path = calibration_dir / "calibration.json"
    calibration = json.loads(calibration_path.read_text())
    calibration["a7_manifest_sha256"] = sha256_file(model_dir / "manifest.json")
    calibration_path.write_text(json.dumps(calibration))
    calibration_manifest_path = calibration_dir / "manifest.json"
    calibration_manifest = json.loads(calibration_manifest_path.read_text())
    calibration_manifest["calibration_sha256"] = sha256_file(calibration_path)
    calibration_manifest["artifact_hashes"]["calibration.json"] = sha256_file(calibration_path)
    calibration_manifest_path.write_text(json.dumps(calibration_manifest))
    monkeypatch.setattr("sipature_ml.evaluation._load_a7_contract", lambda *_: ({}, {}))
    monkeypatch.setattr("sipature_ml.evaluation._canonical_hash", lambda value: value["hash"])
    monkeypatch.setattr("sipature_ml.evaluation.load_config", lambda name: {
        "training": {"indobert": {"hash": "ic", "max_length": 8},
                     "calibration": {"hash": "cc", "ece_bins": 2}},
        "taxonomy": {"aspect_definitions": {"a": {}}},
    }[name])
    calls = []
    output = tmp_path / "evaluation"
    metrics = run_locked_test_evaluation(
        split_dir, model_dir, calibration_dir, output,
        inference_fn=lambda *_: calls.append(1) or {
            "aspect_logits": np.array([[0.0]]), "polarity_logits": np.empty((0, 3)),
            "aspect_latency_seconds": 0.01, "polarity_latency_seconds": 0.0, "device": "mock",
        },
    )
    assert calls == [1]
    assert metrics["aspect"]["macro_f1"] == 0
    assert json.loads((output / "evaluation-state.json").read_text())["status"] == "completed"
    with pytest.raises(FileExistsError):
        run_locked_test_evaluation(split_dir, model_dir, calibration_dir, output)

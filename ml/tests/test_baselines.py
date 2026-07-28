import numpy as np

from sipature_ml.baselines import _tune_thresholds, predict_keyword_labels


def test_keyword_baseline_handles_aspect_polarity_and_severity() -> None:
    taxonomy = {
        "aspect_definitions": {
            "access": {"seed_terms": ["jalan", "akses"]},
            "scenery": {"seed_terms": ["pemandangan"]},
        }
    }
    labels = predict_keyword_labels(
        "Pemandangan bagus tetapi jalan sangat rusak dan berbahaya.", taxonomy
    )
    by_aspect = {label["aspect"]: label for label in labels}
    assert by_aspect["scenery"]["polarity"] == "positive"
    assert by_aspect["access"]["polarity"] == "negative"
    assert by_aspect["access"]["severity"] == "medium"


def test_threshold_tuning_uses_best_validation_f1_per_label() -> None:
    truth = np.array([[1, 0], [1, 0], [0, 1], [0, 1]])
    probabilities = np.array([[0.4, 0.1], [0.45, 0.2], [0.3, 0.6], [0.2, 0.7]])
    thresholds = _tune_thresholds(truth, probabilities, [0.25, 0.35, 0.5, 0.65])
    assert thresholds.tolist() == [0.35, 0.5]

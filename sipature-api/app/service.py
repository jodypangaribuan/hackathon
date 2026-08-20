"""Model loading and review prediction using the frozen SIPATURE production pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sipature_ml.a9 import classify_polarity, load_tfidf_contract
from sipature_ml.config import load_config


class InferenceService:
    """Loads the frozen TF-IDF model once and serves review predictions."""

    def __init__(self, model_dir: Path) -> None:
        self._config = load_config("a9")
        self._taxonomy = load_config("taxonomy")
        self._artifact = load_tfidf_contract(model_dir, self._config)

    @property
    def meta(self) -> dict[str, str]:
        return {
            "a9_version": self._config["a9_version"],
            "aspect_model": self._config["models"]["aspect"]["version"],
            "polarity_version": self._config["models"]["polarity"]["version"],
            "severity_status": self._config["models"]["severity"]["status"],
        }

    def predict(self, text: str) -> list[dict[str, Any]]:
        probabilities = self._artifact["model"].predict_proba(
            self._artifact["vectorizer"].transform([text])
        )[0]
        predictions: list[dict[str, Any]] = []
        for index, aspect in enumerate(self._artifact["aspects"]):
            probability = float(probabilities[index])
            if probability < self._artifact["thresholds"][index]:
                continue
            predictions.append(
                {
                    "aspect": aspect,
                    "aspect_probability": probability,
                    "polarity": classify_polarity(text, aspect, self._taxonomy),
                    "polarity_probability": None,
                    "severity": None,
                }
            )
        return predictions

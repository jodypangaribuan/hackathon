"""C1.6/C1.7 — input validation, latency logging, CPU-only and reload tests."""

from __future__ import annotations

import importlib.util
import json
import logging
from pathlib import Path

from fastapi.testclient import TestClient

REVIEWS_PATH = Path(__file__).parent / "fixtures" / "reviews.json"


def _load_reviews() -> list[dict]:
    return json.loads(REVIEWS_PATH.read_text(encoding="utf-8"))["reviews"]


REVIEWS = _load_reviews()


def _review(review_id: str) -> dict:
    return next(r for r in REVIEWS if r["id"] == review_id)


def test_health_reports_model_versions(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["aspect_model"] == "tfidf-aspect-silver-v1"
    assert body["polarity_version"] == "lexical-polarity-v1"
    assert body["severity_status"] == "unavailable_no_supported_model"


def test_empty_string_rejected(client: TestClient) -> None:
    assert client.post("/predict-review", json={"text": ""}).status_code == 422


def test_whitespace_only_rejected(client: TestClient) -> None:
    assert client.post("/predict-review", json={"text": "   "}).status_code == 400


def test_non_string_rejected(client: TestClient) -> None:
    assert client.post("/predict-review", json={"text": 123}).status_code == 422


def test_too_long_rejected(client: TestClient) -> None:
    assert client.post("/predict-review", json={"text": "x" * 6000}).status_code == 422


def test_valid_negative_prediction(client: TestClient) -> None:
    review = _review("negative_parking_access")
    response = client.post("/predict-review", json={"text": review["text"]})
    assert response.status_code == 200
    body = response.json()
    assert body["model_version"] == "a9-tfidf-lexical-v1.0.4"
    aspects = {pred["aspect"] for pred in body["predictions"]}
    assert "parking" in aspects
    for prediction in body["predictions"]:
        assert prediction["severity"] is None
        assert prediction["polarity_probability"] is None
    parking = next(p for p in body["predictions"] if p["aspect"] == "parking")
    assert parking["polarity"] == "negative"


def test_valid_positive_prediction(client: TestClient) -> None:
    review = _review("positive_scenery_clean")
    response = client.post("/predict-review", json={"text": review["text"]})
    assert response.status_code == 200
    aspects = {pred["aspect"] for pred in response.json()["predictions"]}
    assert "scenery" in aspects


def test_latency_is_logged_without_pii(client: TestClient, caplog) -> None:
    review = _review("negative_parking_access")
    with caplog.at_level(logging.INFO, logger="app.routers.predict"):
        response = client.post("/predict-review", json={"text": review["text"]})
    assert response.status_code == 200
    records = [r for r in caplog.records if r.name == "app.routers.predict"]
    assert records, "expected a latency log line"
    message = records[0].getMessage()
    assert "latency_ms=" in message
    assert "input_chars=" in message
    assert review["text"] not in message


def test_cpu_only_no_gpu_required() -> None:
    assert importlib.util.find_spec("torch") is None

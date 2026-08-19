"""Single-review live prediction endpoint."""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_service
from ..schemas import PredictRequest, PredictResponse
from ..service import InferenceService

router = APIRouter(tags=["predict"])

logger = logging.getLogger(__name__)


@router.post("/predict-review", response_model=PredictResponse)
def predict_review(
    request: PredictRequest,
    service: InferenceService = Depends(get_service),
) -> dict:
    text = " ".join(request.text.split())
    if not text:
        raise HTTPException(status_code=400, detail="text tidak boleh kosong")
    started = time.perf_counter()
    predictions = service.predict(text)
    latency_ms = (time.perf_counter() - started) * 1000.0
    logger.info(
        "predict-review model=%s input_chars=%d predictions=%d latency_ms=%.3f",
        service.meta["a9_version"], len(text), len(predictions), latency_ms,
    )
    return {
        "model_version": service.meta["a9_version"],
        "aspect_model": service.meta["aspect_model"],
        "polarity_version": service.meta["polarity_version"],
        "text": text,
        "predictions": predictions,
    }

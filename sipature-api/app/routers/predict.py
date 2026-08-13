"""Single-review live prediction endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_service
from ..schemas import PredictRequest, PredictResponse
from ..service import InferenceService

router = APIRouter(tags=["predict"])


@router.post("/predict-review", response_model=PredictResponse)
def predict_review(
    request: PredictRequest,
    service: InferenceService = Depends(get_service),
) -> dict:
    text = " ".join(request.text.split())
    if not text:
        raise HTTPException(status_code=400, detail="text tidak boleh kosong")
    return {
        "model_version": service.meta["a9_version"],
        "aspect_model": service.meta["aspect_model"],
        "polarity_version": service.meta["polarity_version"],
        "text": text,
        "predictions": service.predict(text),
    }

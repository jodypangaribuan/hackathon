"""Liveness and model-version endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..dependencies import get_service
from ..schemas import HealthResponse
from ..service import InferenceService

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(service: InferenceService = Depends(get_service)) -> dict:
    return {"status": "ok", **service.meta}

"""Pydantic request/response schemas for the inference API."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .config import settings


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=settings.max_chars)


class Prediction(BaseModel):
    aspect: str
    aspect_probability: float
    polarity: str
    polarity_probability: float | None = None
    severity: str | None = None


class PredictResponse(BaseModel):
    model_version: str
    aspect_model: str
    polarity_version: str
    text: str
    predictions: list[Prediction]


class HealthResponse(BaseModel):
    status: str
    a9_version: str
    aspect_model: str
    polarity_version: str
    severity_status: str

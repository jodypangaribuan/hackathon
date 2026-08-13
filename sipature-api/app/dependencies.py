"""Shared FastAPI dependencies."""

from __future__ import annotations

from fastapi import Request

from .service import InferenceService


def get_service(request: Request) -> InferenceService:
    return request.app.state.service

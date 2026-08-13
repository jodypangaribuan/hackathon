"""SIPATURE inference service entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import settings
from .routers import api_router
from .service import InferenceService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.service = InferenceService(settings.model_dir)
    yield
    app.state.service = None


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    application.include_router(api_router)
    return application


app = create_app()

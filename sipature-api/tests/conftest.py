"""Test fixtures for the inference API.

Run inside the inference container (or any env with fastapi + scikit-learn 1.7.2
+ `sipature_ml` installed) via::

    python -m pytest tests/ -q
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("MODEL_DIR", "/app/model")

from app.main import create_app  # noqa: E402


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

import os
import sys
from pathlib import Path

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://test:test@localhost/test"
)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.routers import ai, ai_feedback, tickets


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(tickets.router)
    app.include_router(ai.router, prefix="/api")
    app.include_router(ai_feedback.router, prefix="/api")
    app.dependency_overrides[get_db] = lambda: object()

    with TestClient(app) as test_client:
        yield test_client

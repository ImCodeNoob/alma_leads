import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("UPLOAD_DIR", "./test_uploads")
os.environ.setdefault("FALLBACK_EMAIL_DIR", "./test_emails")

import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def _clean_state():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    for path in (settings.upload_dir, settings.fallback_email_dir):
        shutil.rmtree(path, ignore_errors=True)
    db_file = Path("./test.db")
    if db_file.exists():
        db_file.unlink()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers(client):
    response = client.post(
        "/api/auth/login",
        json={"email": settings.attorney_email, "password": settings.attorney_password},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

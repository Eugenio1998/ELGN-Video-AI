import pytest
from fastapi.testclient import TestClient
from app.main import app
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))


def test_login_missing_fields():
    response = TestClient(app).post("/api/v1/auth/login", json={})
    assert response.status_code == 422
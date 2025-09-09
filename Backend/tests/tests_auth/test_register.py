import pytest
from fastapi.testclient import TestClient
from app.main import app

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

def test_register_missing_data():
    response = TestClient(app).post("/api/v1/auth/register", json={})
    assert response.status_code == 422
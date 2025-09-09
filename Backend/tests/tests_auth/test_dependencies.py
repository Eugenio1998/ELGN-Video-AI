import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from app.main import app

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))


def test_protected_route_without_token():
    response = TestClient(app).get("/api/v1/auth/me")
    assert response.status_code == 401
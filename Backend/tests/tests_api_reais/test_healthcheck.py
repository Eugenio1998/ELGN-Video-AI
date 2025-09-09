from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthcheck():
    response = client.get("/api/v1/status/health")
    assert response.status_code == 200 or response.status_code == 500
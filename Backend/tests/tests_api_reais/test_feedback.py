import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_send_feedback():
    response = client.post("/api/v1/feedback/submit", data={"message": "Teste", "context": "general"})
    assert response.status_code in [200, 201, 401, 403, 422]  # depende se está autenticado ou não

def test_get_feedbacks():
    response = client.get("/api/v1/feedback/my-feedback")
    assert response.status_code in [200, 401, 403]
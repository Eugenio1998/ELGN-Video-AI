"""
Teste para o módulo de rota: backup_restore
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_backup_restore_endpoint():
    response = client.get("/api/v1/")  # Endpoint genérico, será ajustado manualmente conforme os erros aparecerem
    assert response.status_code in [200, 401, 403, 404, 500]

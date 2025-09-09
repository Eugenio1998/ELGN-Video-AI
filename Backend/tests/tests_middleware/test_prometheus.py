from starlette.testclient import TestClient
from fastapi import FastAPI
from app.middleware.prometheus import PrometheusMiddleware

def test_prometheus_middleware():
    app = FastAPI()
    app.add_middleware(PrometheusMiddleware)

    @app.get("/ping")
    def ping():
        return {"ping": "pong"}

    client = TestClient(app)
    response = client.get("/ping")
    assert response.status_code == 200
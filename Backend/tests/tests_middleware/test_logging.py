from starlette.testclient import TestClient
from fastapi import FastAPI
from app.middleware.logging_middleware import LoggingMiddleware

def test_logging_middleware_runs():
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/")
    def read_root():
        return {"message": "Logged"}

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
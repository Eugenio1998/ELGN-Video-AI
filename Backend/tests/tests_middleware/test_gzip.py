from starlette.testclient import TestClient
from fastapi import FastAPI
from app.middleware.gzip import setup_gzip

def test_gzip_enabled():
    app = FastAPI()
    setup_gzip(app)

    @app.get("/")
    def read_root():
        return "x" * 1000  # Ensure content > 500 bytes

    client = TestClient(app)
    response = client.get("/", headers={"Accept-Encoding": "gzip"})
    assert response.headers.get("Content-Encoding") == "gzip"
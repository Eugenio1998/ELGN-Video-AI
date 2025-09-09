from starlette.testclient import TestClient
from fastapi import FastAPI
from app.middleware.cors import setup_cors

def test_cors_allows_origin():
    app = FastAPI()
    setup_cors(app)

    @app.get("/")
    def read_root():
        return {"msg": "Hello"}

    client = TestClient(app)
    response = client.options("/", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
    assert response.status_code == 200
from starlette.testclient import TestClient
from fastapi import FastAPI
from app.middleware.auth_middleware import AuthMiddleware

def test_auth_middleware_denies_without_token():
    app = FastAPI()
    app.add_middleware(AuthMiddleware)

    @app.get("/video")
    def protected():
        return {"ok": True}

    client = TestClient(app)
    response = client.get("/video")
    assert response.status_code == 401
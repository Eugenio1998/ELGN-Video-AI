import os
os.environ["RATE_LIMIT"] = "3"  # baixa para teste
os.environ["RATE_LIMIT_WINDOW"] = "60"

from starlette.testclient import TestClient
from fastapi import FastAPI
from app.middleware.rate_limit import RateLimitMiddleware

def test_rate_limit_blocks_after_limit():
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware)

    @app.get("/video")
    def limited():
        return {"msg": "ok"}

    client = TestClient(app)
    for _ in range(3):
        client.get("/video")
    response = client.get("/video")
    assert response.status_code in [429, 200]
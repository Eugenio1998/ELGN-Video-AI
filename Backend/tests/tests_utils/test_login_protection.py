from app.utils import login_protection

def test_redis_connection():
    assert login_protection.redis_conn is not None

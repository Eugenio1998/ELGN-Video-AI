from app.models.user import User, UserRole

def test_user_model():
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        is_active=True,
        role=UserRole.USER 
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.role == UserRole.USER

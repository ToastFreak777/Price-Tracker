from ptracker.auth.service import AuthService
import pytest


def test_register_success(app):
    expected = {"username": "alice", "email": "alice@test.com"}

    service = AuthService()
    user = service.register_user(**expected, password="pass123")

    assert user.username == expected["username"]
    assert user.email == expected["email"]
    assert user.role == "user"  # Default role
    assert user.password_hash != "pass123"  # Hashed, not plaintext
    assert user.password_hash.startswith("scrypt:")  # Check hash format


@pytest.mark.parametrize(
    "username, email",
    [("uniqueUsername", "test@example.com"), ("testuser", "unique@example.com")],
)
def test_register_user_fails_on_duplicate(auth_user, username, email):
    service = AuthService()
    with pytest.raises(ValueError, match="Username or email already exists"):
        service.register_user(username, email, "newpass123")


def test_login_success(auth_user):
    service = AuthService()
    user = service.login("test@example.com", "password123")

    assert user.id == auth_user.id
    assert user.email == auth_user.email


@pytest.mark.parametrize(
    "email, password",
    [
        ("test@example.com", "wrongpassword123"),
        ("wrong@example.com", "password123"),
    ],
)
def test_login_user_fails(auth_user, email, password):
    service = AuthService()
    with pytest.raises(ValueError, match="Invalid credentials"):
        service.login(email, password)

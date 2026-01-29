from ptracker.auth.service import AuthService


def test_register_user_returns_user_with_correct_data(app):
    with app.app_context():
        service = AuthService()
        user = service.register_user("alice", "alice@test.com", "pass123")

        assert user.username == "alice"
        assert user.email == "alice@test.com"
        assert user.password_hash != "pass123"  # Hashed, not plaintext
        assert user.password_hash.startswith("scrypt:")  # Check hash format


def test_login_user_returns_user_with_corrct_data(auth_user):
    service = AuthService()
    user = service.login("test@example.com", "password123")

    assert user.id == auth_user.id
    assert user.email == auth_user.email

import pytest
from werkzeug.security import generate_password_hash

from ptracker import create_app
from ptracker.extensions import db
from ptracker.models import User


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_user(app):
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=generate_password_hash("password123"),
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_client(client, auth_user):
    # Log in via API
    client.post(
        "/auth/login",
        json={"email": auth_user.email, "password": "password123"},
    )
    return client

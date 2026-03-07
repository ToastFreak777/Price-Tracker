import pytest
from werkzeug.security import generate_password_hash

from ptracker import create_app
from ptracker.extensions import db
from ptracker.models import User, Item, PriceHistory


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False
    SERVER_NAME = "localhost"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


def login_client(client, email, password):
    client.post("/auth/login", json={"email": email, "password": password})
    return client


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
def client_with_user(client, auth_user):
    """Client with a user in the database but not logged in"""
    return client


@pytest.fixture
def auth_client(client, auth_user):
    """Client with a user logged in"""
    return login_client(client, auth_user.email, "password123")


@pytest.fixture
def auth_client_demo(client):
    user = User(
        username="demo_user",
        email="demo@example.com",
        role="demo",
        password_hash=generate_password_hash("demo123"),
    )
    db.session.add(user)
    db.session.commit()

    return login_client(client, user.email, "demo123")


@pytest.fixture
def item_no_history(app):
    item = Item(vendor="mock", external_id="123", url="https://mock.com/items/123", current_price=100.0)
    db.session.add(item)
    db.session.flush()

    history = PriceHistory(item_id=item.id, price=100.0)
    db.session.add(history)
    db.session.commit()

    return item


@pytest.fixture
def item_with_history(item_no_history):
    item_no_history.current_price = 90
    db.session.flush()

    history = PriceHistory(item_id=item_no_history.id, price=item_no_history.current_price)
    db.session.add(history)
    db.session.commit()

    return item_no_history

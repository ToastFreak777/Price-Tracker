def test_register_login_logout_flow(client):
    # Register
    res = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "secret123",
        },
    )
    assert res.status_code == 201
    assert res.get_json()["success"] is True

    # Login should now conflict because already logged in
    res = client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "secret123"},
    )
    assert res.status_code == 409

    # Logout
    res = client.post("/auth/logout")
    assert res.status_code == 200

    # Login again after logout
    res = client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "secret123"},
    )
    assert res.status_code == 200
    assert res.get_json()["success"] is True


def test_register_user_raises_on_duplicate_username(client_with_user):
    # Register duplicate user
    res = client_with_user.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "password123",
        },
    )
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert "Username or email already exists" in data["error"]


def test_register_user_raises_on_duplicate_email(client_with_user):
    # Register duplicate user
    res = client_with_user.post(
        "/auth/register",
        json={
            "username": "test2user",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert "Username or email already exists" in data["error"]


def test_register_route_successfully_registers_user(client):
    user = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123",
    }

    res = client.post("/auth/register", json=user)

    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["username"] == user["username"]
    assert data["data"]["email"] == user["email"]


def test_register_route_rejects_logged_in_user(auth_client):
    # Attempt to register while logged in
    user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }

    res = auth_client.post("/auth/register", json=user)
    assert res.status_code == 409
    data = res.get_json()
    assert data["success"] is False
    assert "User is already registered" in data["error"]


def test_login_rejects_wrong_password(client_with_user):
    # Attempt login with wrong password
    res = client_with_user.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )

    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert "Invalid credentials" in data["error"]


def test_login_rejects_wrong_email(client_with_user):
    # Attempt login with wrong email
    res = client_with_user.post(
        "/auth/login",
        json={"email": "wrong@example.com", "password": "password123"},
    )

    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert "Invalid credentials" in data["error"]


def test_login__route_rejects_logged_in_user(auth_client):
    # Attempt to register while logged in
    user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }

    res = auth_client.post("/auth/login", json=user)
    assert res.status_code == 409
    data = res.get_json()
    assert data["success"] is False
    assert "User is already logged in" in data["error"]


def test_login_route_sucessfully_logs_in(client_with_user):
    user = {"email": "test@example.com", "password": "password123"}

    res = client_with_user.post("/auth/login", json=user)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["email"] == user["email"]


def test_logout_route_rejects_unregistered_user(client):
    res = client.post("/auth/logout")

    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False
    assert "No user is currently logged in" in data["error"]


def test_delete_user_with_incorrect_user(auth_client):
    # User executing command id != 69
    res = auth_client.delete("/auth/user/69")

    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert "Cannot delete another user's account" in data["error"]

class TestLoginPage:
    def test_login_page_renders_with_form_fields(self, client):
        res = client.get("/auth/login")
        assert res.status_code == 200
        assert b"Login" in res.data
        assert b'name="email"' in res.data
        assert b'name="password"' in res.data
        assert b'type="submit"' in res.data

    def test_login_page_redirects_authenticated_user(self, auth_client):
        # auth_client is already logged in
        res = auth_client.get("/auth/login")
        assert res.status_code == 302  # redirect
        assert res.headers["Location"].endswith("/home")

    def test_login_form_submission_success(self, client, auth_user):
        res = client.post(
            "/auth/login",
            data={"email": auth_user.email, "password": "password123"},
            follow_redirects=True,
        )

        assert res.status_code == 200
        assert b"Home" in res.data

    def test_login_form_submission_wrong_password(self, client, auth_user):
        res = client.post(
            "/auth/login",
            data={"email": auth_user.email, "password": "wrongpassword"},
        )

        assert b"Invalid credentials" in res.data

    def test_login_redirects_to_next_page(self, client, auth_user):
        next_url = "/dashboard"
        res = client.post(
            f"/auth/login?next={next_url}",
            data={"email": auth_user.email, "password": "password123"},
            follow_redirects=False,
        )

        assert res.status_code == 302
        assert res.headers["Location"].endswith(next_url)


class TestRegisterPage:

    def test_register_page_renders_with_form_fields(self, client):
        res = client.get("/auth/register")
        assert res.status_code == 200
        assert b"Register" in res.data
        assert b'name="username"' in res.data
        assert b'name="email"' in res.data
        assert b'name="password"' in res.data
        assert b'name="confirm_password"' in res.data
        assert b'type="submit"' in res.data

    def test_register_page_redirects_authenticated_user(self, auth_client):
        # auth_client is already logged in
        res = auth_client.get("/auth/register")
        assert res.status_code == 302  # redirect
        assert res.headers["Location"].endswith("/home")

    def test_register_form_submission_success(self, client):
        res = client.post(
            "/auth/register",
            data={
                "username": "testuser",
                "email": "test@test.com",
                "password": "password123",
                "confirm_password": "password123",
            },
            follow_redirects=True,
        )

        assert res.status_code == 200
        assert b"Home" in res.data

    def test_register_form_submission_password_mismatch(self, client):
        res = client.post(
            "/auth/register",
            data={
                "username": "testuser",
                "email": "test@test.com",
                "password": "password123",
                "confirm_password": "wrongpassword",
            },
        )

        assert b"Passwords must match" in res.data

    def test_register_form_submission_duplicate_email(self, client, auth_user):
        res = client.post(
            "/auth/register",
            data={
                "username": "newuser",
                "email": auth_user.email,
                "password": "password123",
                "confirm_password": "password123",
            },
        )

        assert b"Username or email already exists" in res.data


class TestAddProductPage:
    def test_add_product_requires_auth(self, client):
        res = client.get("/items/add")
        assert res.status_code == 302
        assert "/auth/login" in res.location


class TestAuthAPI:

    def test_register_login_logout_flow(self, client):
        # Register
        res = client.post(
            "/api/register",
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
            "/api/login",
            json={"email": "alice@example.com", "password": "secret123"},
        )
        assert res.status_code == 409

        # Logout
        res = client.post("/api/logout")
        assert res.status_code == 200

        # Login again after logout
        res = client.post(
            "/api/login",
            json={"email": "alice@example.com", "password": "secret123"},
        )
        assert res.status_code == 200
        assert res.get_json()["success"] is True

    def test_register_user_raises_on_duplicate_username(self, client_with_user):
        # Register duplicate user
        res = client_with_user.post(
            "/api/register",
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

    def test_register_user_raises_on_duplicate_email(self, client_with_user):
        # Register duplicate user
        res = client_with_user.post(
            "/api/register",
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

    def test_register_route_successfully_registers_user(self, client):
        user = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        }

        res = client.post("/api/register", json=user)

        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["username"] == user["username"]
        assert data["data"]["email"] == user["email"]

    def test_register_route_rejects_logged_in_user(self, auth_client):
        # Attempt to register while logged in
        user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        }

        res = auth_client.post("/api/register", json=user)
        assert res.status_code == 409
        data = res.get_json()
        assert data["success"] is False
        assert "User is already registered" in data["error"]

    def test_login_rejects_wrong_password(self, client_with_user):
        # Attempt login with wrong password
        res = client_with_user.post(
            "/api/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )

        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert "Invalid credentials" in data["error"]

    def test_login_rejects_wrong_email(self, client_with_user):
        # Attempt login with wrong email
        res = client_with_user.post(
            "/api/login",
            json={"email": "wrong@example.com", "password": "password123"},
        )

        assert res.status_code == 400
        data = res.get_json()
        assert data["success"] is False
        assert "Invalid credentials" in data["error"]

    def test_login__route_rejects_logged_in_user(self, auth_client):
        # Attempt to register while logged in
        user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        }

        res = auth_client.post("/api/login", json=user)
        assert res.status_code == 409
        data = res.get_json()
        assert data["success"] is False
        assert "User is already logged in" in data["error"]

    def test_login_route_sucessfully_logs_in(self, client_with_user):
        user = {"email": "test@example.com", "password": "password123"}

        res = client_with_user.post("/api/login", json=user)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["email"] == user["email"]

    def test_logout_route_rejects_unregistered_user(self, client):
        res = client.post("/api/logout")

        assert res.status_code == 401
        data = res.get_json()
        assert data["success"] is False
        assert "No user is currently logged in" in data["error"]

    def test_delete_user_with_incorrect_user(self, auth_client):
        # User executing command id != 69
        res = auth_client.delete("/api/user/69")

        assert res.status_code == 403
        data = res.get_json()
        assert data["success"] is False
        assert "Cannot delete another user's account" in data["error"]

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
        assert "/home" in res.location

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
        assert next_url in res.location


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
        assert "/home" in res.location

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

    def test_register_form_submission_duplicate_username(self, client, auth_user):
        res = client.post(
            "/auth/register",
            data={
                "username": auth_user.username,
                "email": "test@test.com",
                "password": "password123",
                "confirm_password": "password123",
            },
        )

        assert b"Username or email already exists" in res.data


class TestForgotPasswordPage:
    def test_forgot_password_page_renders(self, client):
        res = client.get("/auth/forgot-password")
        assert res.status_code == 200
        assert b"Forgot Password" in res.data

    def test_forgot_password_page_redirects_authenticated_user(self, auth_client):
        # auth_client is already logged in
        res = auth_client.get("/auth/forgot-password")
        assert res.status_code == 302  # redirect
        assert "/home" in res.location


class TestLogoutRoute:
    def test_logout_route_logs_out_user(self, auth_client):
        res = auth_client.get("/auth/logout")
        assert res.status_code == 302
        assert "/auth/login" in res.location


class TestSettingsPage:
    def test_settings_page_requires_auth(self, client):
        res = client.get("/auth/user/settings")
        assert res.status_code == 302
        assert "/auth/login" in res.location


class TestAddProductPage:
    def test_add_product_requires_auth(self, client):
        res = client.get("/items/add")
        assert res.status_code == 302
        assert "/auth/login" in res.location


def test_demo_session(client):
    res = client.post("/auth/demo")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "/home" in data["redirect"]

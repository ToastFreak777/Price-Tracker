import pytest


class TestRegisterAPI:
    def test_register_api_creates_user_successfully(self, client):
        res = client.post(
            "/api/register",
            json={
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "password123",
            },
        )
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["username"] == "newuser"
        assert data["data"]["email"] == "newuser@test.com"

    def test_register_api_fails_when_already_authenticated(self, auth_client):
        res = auth_client.post(
            "/api/register",
            json={
                "username": "anotheruser",
                "email": "another@test.com",
                "password": "password123",
            },
        )
        assert res.status_code == 409

    @pytest.mark.parametrize(
        "username, email",
        [
            ("testuser", "test2@example.com"),
            ("test2user", "test@example.com"),
        ],
        ids=["duplicate_username", "duplicate_email"],
    )
    def test_register_api_fails_on_duplicate(self, client_with_user, username, email):
        res = client_with_user.post(
            "/api/register",
            json={
                "username": username,
                "email": email,
                "password": "password123",
            },
        )
        assert res.status_code == 400

    def test_register_login_logout_flow(self, client):
        user = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "secret123",
        }

        # Register
        res = client.post(
            "/api/register",
            json=user,
        )
        assert res.status_code == 201

        # Login should now conflict because already logged in
        res = client.post(
            "/api/login",
            json={"email": user["email"], "password": user["password"]},
        )
        assert res.status_code == 409

        # Logout
        res = client.post("/api/logout")
        assert res.status_code == 200

        # Login again after logout
        res = client.post(
            "/api/login",
            json={"email": user["email"], "password": user["password"]},
        )
        assert res.status_code == 200


class TestLoginAPI:
    def test_login_api_authenticates_user(self, client, auth_user):
        res = client.post(
            "/api/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["email"] == auth_user.email

    @pytest.mark.parametrize(
        "email, password",
        [
            ("test@example.com", "wrongpassword"),
            ("wrong@example.com", "password123"),
        ],
        ids=["wrong_password", "wrong_email"],
    )
    def test_login_api_fails_with_invalid_credentials(self, client, auth_user, email, password):
        res = client.post(
            "/api/login",
            json={"email": email, "password": password},
        )
        assert res.status_code == 400

    def test_login_api_fails_when_already_authenticated(self, auth_client):
        res = auth_client.post(
            "/api/login",
            json={"email": "test@example.com", "password": "password123"},
        )
        assert res.status_code == 409


class TestLogoutAPI:
    def test_logout_api_logs_out_user(self, auth_client):
        res = auth_client.post("/api/logout")
        assert res.status_code == 200

    def test_logout_api_fails_when_not_authenticated(self, client):
        res = client.post("/api/logout")
        assert res.status_code == 401


class TestDeleteUserAPI:
    def test_delete_user_removes_account(self, auth_client, auth_user):
        res = auth_client.delete(f"/api/user/{auth_user.id}")
        assert res.status_code == 200

    def test_delete_user_requires_authentication(self, client):
        res = client.delete("/api/user/1")
        assert res.status_code == 302

    def test_delete_user_fails_for_other_users(self, auth_client, auth_user):
        # Try to delete a different user's account
        res = auth_client.delete(f"/api/user/{auth_user.id + 999}")
        assert res.status_code == 403


class TestGetItemAPI:
    def test_get_item_returns_item_data(self, auth_client):
        # First track an item
        res = auth_client.post(
            "api/items/add",
            json={"url": "https://mock.com/items/789", "target_price": 75.0},
        )

        item_id = res.get_json()["data"]["id"]

        # Get item via API
        res = auth_client.get(f"/api/items/{item_id}")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["id"] == item_id

    def test_get_item_requires_authentication(self, client):
        res = client.get("/api/items/1")
        assert res.status_code == 302


class TestUntrackItemAPI:
    def test_untrack_item_removes_item(self, auth_client):
        # First track an item
        res = auth_client.post(
            "/api/items/add",
            json={"url": "https://mock.com/items/321", "target_price": 60.0},
        )
        item_id = res.get_json()["data"]["id"]

        # Untrack the item
        res = auth_client.delete(f"/api/items/{item_id}")
        assert res.status_code == 200

    def test_untrack_item_requires_authentication(self, client):
        res = client.delete("/api/items/1")
        assert res.status_code == 302


class TestUpdateNotificationsAPI:
    def test_update_user_notifications(self, auth_client):
        res = auth_client.patch(
            "/api/user/notifications",
            json={"enabled": False},
        )
        assert res.status_code == 200

    def test_update_item_notifications(self, auth_client):
        # First track an item
        res = auth_client.post(
            "/items",
            json={"url": "https://mock.com/items/111", "target_price": 40.0},
        )
        item_id = res.get_json()["item_id"]

        # Update item notifications
        res = auth_client.patch(
            f"/api/items/{item_id}/notifications",
            json={"enabled": False},
        )
        assert res.status_code == 200


class TestUpdateAllItemsAPI:
    def test_update_all_items_endpoint(self, client):
        res = client.get("/api/update-items")
        assert res.status_code == 200

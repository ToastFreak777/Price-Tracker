import pytest


class TestAddProductPage:
    def test_add_product_page_renders_for_authenticated_user(self, auth_client):
        res = auth_client.get("/items/add")
        assert res.status_code == 200
        assert b"Add Product" in res.data
        assert b'name="product_url"' in res.data
        assert b'name="target_price"' in res.data

    def test_add_product_page_redirects_unauthenticated_user(self, client):
        res = client.get("/items/add", follow_redirects=False)
        assert res.status_code == 302
        assert "/auth/login" in res.location

    def test_add_product_form_submission_success(self, auth_client):
        res = auth_client.post(
            "/items/add",
            data={
                "product_url": "https://mock.com/items/123",
                "target_price": 50.0,
                "csrf_token": auth_client.application.config.get("WTF_CSRF_ENABLED", False),
            },
            follow_redirects=True,
        )
        assert res.status_code == 200
        assert b"Home" in res.data


class TestAlertsPage:
    def test_alerts_page_renders_for_authenticated_user(self, auth_client):
        res = auth_client.get("/items/alerts")
        assert res.status_code == 200
        assert b"Alerts" in res.data

    def test_alerts_page_redirects_unauthenticated_user(self, client):
        res = client.get("/items/alerts", follow_redirects=False)
        assert res.status_code == 302
        assert "/auth/login" in res.location


class TestTrackItemAPI:
    def test_track_item_creates_item_successfully(self, auth_client):
        res = auth_client.post(
            "/items",
            json={"url": "https://mock.com/items/123", "target_price": 50.0},
        )
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert "item_id" in data
        assert data["vendor"] == "mock"

    def test_track_item_requires_authentication(self, client):
        res = client.post(
            "/items",
            json={"url": "https://mock.com/items/123", "target_price": 50.0},
        )
        assert res.status_code == 302  # Redirect to login


class TestGetItemDetails:
    def test_get_item_details_renders_page(self, auth_client):
        # First add an item to track
        res = auth_client.post(
            "/items",
            json={"url": "https://mock.com/items/456", "target_price": 100.0},
        )
        item_id = res.get_json()["item_id"]

        # Get item details page
        res = auth_client.get(f"/items/{item_id}")
        assert res.status_code == 200
        assert b"Mock Product" in res.data

    def test_get_item_details_requires_authentication(self, client):
        res = client.get("/items/1", follow_redirects=False)
        assert res.status_code == 302
        assert "/auth/login" in res.location

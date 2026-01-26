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

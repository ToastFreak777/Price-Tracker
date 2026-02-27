def test_price_tracking_flow(auth_client):
    # Add item using mock datasource URL
    res = auth_client.post(
        "/items",
        json={"url": "https://mock.com/items/123", "target_price": 50.0},
    )
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    item_id = data["item_id"]

    # List items for user
    res = auth_client.get("/items")
    assert res.status_code == 200
    items = res.get_json()["data"]
    assert any(i["item"]["id"] == item_id for i in items)

    # Get item details (snapshot + history)
    res = auth_client.get(f"/items/{item_id}")
    assert res.status_code == 200
    payload = res.get_json()["data"]
    assert payload["id"] == item_id
    assert "price_history" in payload

    # Untrack item
    res = auth_client.delete(f"/items/{item_id}")
    assert res.status_code == 200

    # List again to ensure removed
    res = auth_client.get("/items")
    assert res.status_code == 200
    items = res.get_json()["data"]
    assert all(i["item"]["id"] != item_id for i in items)

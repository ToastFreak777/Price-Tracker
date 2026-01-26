import json
from flask import Blueprint, request, jsonify
from ptracker.services.price_tracker import PriceTrackerService
from ptracker.api.rapid import search

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
def home():
    return "<h1>Price Tracker Home page</h1>"


@main.route("/items", methods=["GET"])
def get_items():
    """Get all items user is tracking"""

    user_id = 1  # I'll add this later when auth is implemented
    service = PriceTrackerService()

    try:
        results = service.get_items(user_id)
        serialized_items = [
            {
                "user_item_id": ui.id,
                "target_price": ui.target_price,
                "item": {
                    "id": ui.item.id,
                    "vendor": ui.item.vendor,
                    "external_id": ui.item.external_id,
                    "url": ui.item.url,
                },
            }
            for ui in results
        ]

        return jsonify({"success": True, "data": serialized_items}), 200
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@main.route("/items", methods=["POST"])
def add_item():
    """Add a new item to track"""
    data = request.get_json()
    url = data.get("url")
    target_price = data.get("target_price")
    user_id = 1  # I'll add this later when auth is implemented

    try:
        service = PriceTrackerService()
        item = service.add_item(url, user_id, target_price)
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Item added to tracking",
                    "item_id": item.id,
                    "vendor": item.vendor,
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@main.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    try:
        service = PriceTrackerService()
        result = service.get_item(item_id)

        snapshot = result["snapshot"]
        if snapshot.timestamp:
            snapshot.timestamp = snapshot.timestamp.isoformat()

        serialized_history = [
            {
                "price": h.price,
                "timestamp": h.timestamp.isoformat(),
            }
            for h in result["price_history"]
        ]

        return (
            jsonify(
                {
                    "success": True,
                    "data": {
                        "id": item_id,
                        "snapshot": result["snapshot"],
                        "price_history": serialized_history,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@main.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    # TODO: Remove item from user's tracked list'
    return jsonify({"message": f"Item {item_id} deleted"}), 200


# Redundant with get_item for now, may be useful if I add query parameters later
# @main.route("/items/<int:item_id>/history", methods=["GET"])
# def get_price_history(item_id):
#     return f"<h1>Price history for item {item_id}</h1>"


@main.route("/test/products")
def products():
    products = search("Razor Deathadder V2 Pro")

    for product in products[:5]:
        print(product.get("title"))
        print(product.get("price_cents"))
        print(product.get("availability"))
        print(product.get("url"))
        print("-----")

    return "<h1>Products page</h1>"

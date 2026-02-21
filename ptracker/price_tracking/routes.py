from flask import Blueprint, request, jsonify, g, render_template
from flask_login import current_user, login_required

price_bp = Blueprint("price", __name__, url_prefix="/items")


@price_bp.route("/add")
def add_product_page():
    return render_template("product/add_product.html", title="Add Product", current_path=request.path)


@price_bp.route("", methods=["GET"])
@login_required
def get_items():
    """Get all items user is tracking"""

    results = g.price_service.get_items(current_user.id)
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


@price_bp.route("", methods=["POST"])
@login_required
def track_item():
    """Add a new item to track"""
    data = request.get_json()
    url = data.get("url")
    target_price = data.get("target_price")
    item = g.price_service.track_item(url, current_user.id, target_price)
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


@price_bp.route("/<int:item_id>", methods=["GET"])
@login_required
def get_item(item_id):
    result = g.price_service.get_item(item_id)

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


@price_bp.route("/<int:item_id>", methods=["DELETE"])
@login_required
def untrack_item(item_id):

    g.price_service.remove_item(current_user.id, item_id)
    return jsonify({"message": f"Item {item_id} untracked"}), 200


# Redundant with get_item for now, may be useful if I add query parameters later
# @main.route("/items/<int:item_id>/history", methods=["GET"])
# def get_price_history(item_id):
#     return f"<h1>Price history for item {item_id}</h1>"

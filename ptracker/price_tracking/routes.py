from flask import Blueprint, request, jsonify, g, render_template, redirect, url_for
from flask_login import current_user, login_required

from ptracker.price_tracking.forms import TrackProductForm

price_bp = Blueprint("price", __name__, url_prefix="/items")

product = {"name": "Sony WH-1000XM4", "price": 299.99, "price_drop": 8.0}
products = [product for _ in range(7)]


@price_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_product_page():
    form = TrackProductForm()

    if form.validate_on_submit():
        target_price = 500  # Placeholder until I add this to the form
        g.price_service.track_item(form.product_url.data, current_user.id, target_price)
        return redirect(url_for("main.home_page"))

    return render_template("product/add_product.html", title="Add Product", current_path=request.path, form=form)


@price_bp.route("/alerts")
def notifications_page():
    return render_template("product/alerts.html", title="Alerts", current_path=request.path, products=products)


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

    item = result["item"]
    last_fetched_iso = None
    if item.last_fetched:
        last_fetched_iso = item.last_fetched.isoformat()

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
                    "item": {
                        "id": item.id,
                        "vendor": item.vendor,
                        "external_id": item.external_id,
                        "url": item.url,
                        "name": item.name,
                        "currency": item.currency,
                        "current_price": item.current_price,
                        "image_url": item.image_url,
                        "in_stock": item.in_stock,
                        "last_fetched": last_fetched_iso,
                    },
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

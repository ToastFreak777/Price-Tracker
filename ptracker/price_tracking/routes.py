from flask import Blueprint, request, jsonify, g, render_template, redirect, url_for
from flask_login import current_user, login_required

from ptracker.price_tracking.forms import TrackProductForm, ItemDetailsForm
from ptracker.price_tracking.service import PriceTrackerService

price_bp = Blueprint("price", __name__, url_prefix="/items")


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
    service = PriceTrackerService()
    products = service.get_user_tracked_items(current_user.id, refresh_stale=False)

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


@price_bp.route("/<int:item_id>", methods=["GET", "POST"])
@login_required
def get_item(item_id):
    data = g.price_service.get_user_item(current_user.id, item_id)
    item = data["item"]
    target_price = data["target_price"]
    price_change = data["price_change"]

    # last_fetched_iso = None
    # if item.last_fetched:
    #     last_fetched_iso = item.last_fetched.isoformat()

    serialized_history = [
        {
            "price": h.price,
            "timestamp": h.timestamp.strftime("%b %d, %Y"),
        }
        for h in item.price_history
    ]

    form = ItemDetailsForm()

    if form.validate_on_submit():
        g.price_service.update_item_target_price(current_user.id, item_id, form.alert_price.data)

    return render_template(
        "product/product_details.html",
        title=item.name,
        current_path=request.path,
        item=item,
        target_price=target_price,
        price_change=price_change,
        price_history=serialized_history,
        form=form,
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

from flask import Blueprint, request, jsonify, g, render_template, redirect, url_for
from flask_login import current_user, login_required

from ptracker.price_tracking.forms import TrackProductForm, ItemDetailsForm, DeleteItemForm
from ptracker.price_tracking.service import PriceTrackerService

price_bp = Blueprint("price", __name__, url_prefix="/items")


@price_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_product_page():
    form = TrackProductForm()

    if form.validate_on_submit():
        g.price_service.track_item(form.product_url.data, current_user.id, form.target_price.data)
        return redirect(url_for("main.home_page"))

    return render_template("product/add_product.html", title="Add Product", current_path=request.path, form=form)


@price_bp.route("/alerts", methods=["GET", "POST"])
@login_required
def notifications_page():
    form = DeleteItemForm()

    if form.validate_on_submit():
        g.price_service.remove_item(current_user.id, form.item_id.data)

    service = PriceTrackerService()
    products = service.get_user_tracked_items(current_user.id, refresh_stale=False)

    return render_template(
        "product/alerts.html", title="Alerts", current_path=request.path, products=products, form=form
    )


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
    form = ItemDetailsForm()
    delete_form = DeleteItemForm()

    if delete_form.validate_on_submit():
        g.price_service.remove_item(current_user.id, item_id)
        return redirect(url_for("main.home_page"))

    if form.validate_on_submit():
        g.price_service.update_item_target_price(current_user.id, item_id, form.alert_price.data)

    data = g.price_service.get_user_item(current_user.id, item_id)
    item = data["item"]
    target_price = data["target_price"]
    price_change = data["price_change"]

    serialized_history = [
        {
            "price": h.price,
            "timestamp": h.timestamp.strftime("%b %d, %Y"),
        }
        for h in item.price_history
    ]

    return render_template(
        "product/product_details.html",
        title=item.name,
        current_path=request.path,
        item=item,
        target_price=target_price,
        price_change=price_change,
        price_history=serialized_history,
        form=form,
        delete_form=delete_form,
    )

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from ptracker.price_tracking.service import PriceTrackerService


main_bp = Blueprint("main", __name__)

product = {"name": "Sony WH-1000XM4", "price": 299.99, "price_drop": 8.0}
products = [product for _ in range(7)]


@main_bp.route("/")
@main_bp.route("/home")
@login_required
def home_page():
    service = PriceTrackerService()
    # products = service.get_user_tracked_items(current_user.id, refresh_stale=True)
    return render_template("main/home.html", title="Home", products=products, current_path=request.path)

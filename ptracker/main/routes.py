from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from ptracker.price_tracking.service import PriceTrackerService

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@main_bp.route("/home")
@login_required
def home_page():
    service = PriceTrackerService()
    products = service.get_user_tracked_items(current_user.id, refresh_stale=False)
    return render_template("main/home.html", title="Home", products=products, current_path=request.path)

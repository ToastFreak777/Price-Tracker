from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)

product = {"name": "Sony WH-1000XM4", "price": 299.99, "price_drop": 8.0}
products = [product for _ in range(5)]


@main_bp.route("/")
@main_bp.route("/home")
def home():
    return render_template("main/home.html", title="Home", products=products)

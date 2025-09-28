from flask import Blueprint

from ptracker.api.rapid import search

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
def home():
    return "<h1>Price Tracker Home page</h1>"


@main.route("/products")
def products():
    products = search("Razor Deathadder V2 Pro")

    for product in products[:5]:
        print(product.get("title"))
        print(product.get("price_cents"))
        print(product.get("availability"))
        print(product.get("url"))
        print("-----")

    return "<h1>Products page</h1>"

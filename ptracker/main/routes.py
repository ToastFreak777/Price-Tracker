from flask import Blueprint

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
def home():
    return "<h1>Price Tracker Home page</h1>"

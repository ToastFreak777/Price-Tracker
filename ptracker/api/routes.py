from flask import Blueprint, request, jsonify, g
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.exceptions import Conflict, Unauthorized, Forbidden

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/register", methods=["POST"])
def register():

    if current_user.is_authenticated:
        raise Conflict("User is already registered")

    data = request.get_json() or {}
    user = g.auth_service.register_user(data["username"], data["email"], data["password"])
    login_user(user, remember=False)
    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            }
        ),
        201,
    )


@api_bp.route("/login", methods=["POST"])
def login():

    if current_user.is_authenticated:
        raise Conflict("User is already logged in")
    data = request.get_json()
    user = g.auth_service.login(data["email"], data["password"])
    login_user(user, remember=False)
    return (
        jsonify(
            {
                "success": True,
                "data": {"username": user.username, "email": user.email},
            }
        ),
        200,
    )


@api_bp.route("/logout", methods=["POST"])
def logout():
    if not current_user.is_authenticated:
        raise Unauthorized("No user is currently logged in")
    logout_user()
    return jsonify({"success": True, "message": "User logged out"}), 200


@api_bp.route("/user/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id: int):
    if current_user.id != user_id:
        raise Forbidden("Cannot delete another user's account")
    g.auth_service.delete_user(user_id)
    return jsonify({"success": True, "message": "User's Account Deleted"}), 200


@api_bp.route("/items")
@login_required
def get_items():
    """Get all items user is tracking"""
    pass

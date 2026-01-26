from flask import Blueprint, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.exceptions import Conflict, Unauthorized
from .service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register_route():

    if current_user.is_authenticated:
        raise Conflict("User is already registered")

    data = request.get_json() or {}
    service = AuthService()
    user = service.register_user(data["username"], data["email"], data["password"])
    login_user(user, remember=False)
    return jsonify(
        {
            "success": True,
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        },
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login_route():

    if current_user.is_authenticated:
        raise Conflict("User is already logged in")
    data = request.get_json()
    service = AuthService()
    user = service.login(data["email"], data["password"])
    login_user(user, remember=False)
    return jsonify({"success": True, "data": data}, 200)


@auth_bp.route("/logout", methods=["POST"])
def logout_route():
    if not current_user.is_authenticated:
        raise Unauthorized("No user is currently logged in")
    logout_user()
    return jsonify({"success": True, "message": "User logged out"}, 200)


# @auth_bp.route("/user/<int:user_id>", methods=["GET"])
# def get_user(user_id: str):
#         return jsonify({"success": True, "data": data})


# @auth_bp.route("/user/<int:user_id>/password", methods=["PUT"])
# def change_password(user_id: int):
#         return jsonify({"success": True, "data": data})


@auth_bp.route("/user/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id: int):
    if current_user.id != user_id:
        raise ValueError("Cannot delete another user's account")
    service = AuthService()
    service.delete_user(user_id)
    return jsonify({"success": True, "message": "User's Account Deleted"}, 200)

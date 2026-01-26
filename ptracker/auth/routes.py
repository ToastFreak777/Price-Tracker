from flask import Blueprint, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from .service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register_route():

    try:
        if current_user.is_authenticated:
            return (
                jsonify({"success": False, "message": "user is already logged in"}),
                401,
            )

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
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login_route():

    try:
        if current_user.is_authenticated:
            return jsonify(
                {"success": False, "message": "user is already logged in"}, 401
            )
        data = request.get_json()
        service = AuthService()
        user = service.login(data["email"], data["password"])
        login_user(user, remember=False)
        return jsonify({"success": True, "data": data}, 200)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@auth_bp.route("/logout", methods=["POST"])
def logout_route():
    try:
        if not current_user.is_authenticated:
            return jsonify({"success": False, "message": "No user logged in"}, 401)
        logout_user()
        return jsonify({"success": True, "message": "User logged out"}, 200)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400


# @auth_bp.route("/user/<int:user_id>", methods=["GET"])
# def get_user(user_id: str):
#     try:
#         return jsonify({"success": True, "data": data})
#     except ValueError as e:
#         return jsonify({"success": False, "error": str(e)}), 400


# @auth_bp.route("/user/<int:user_id>/password", methods=["PUT"])
# def change_password(user_id: int):
#     try:
#         return jsonify({"success": True, "data": data})
#     except ValueError as e:
#         return jsonify({"success": False, "error": str(e)}), 400


@auth_bp.route("/user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int):
    service = AuthService()

    try:
        service.delete_user(user_id)
        return jsonify({"success": True, "message": "User's Account Deleted"}, 200)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

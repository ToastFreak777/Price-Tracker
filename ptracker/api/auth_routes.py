from flask import g
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.exceptions import Conflict, Unauthorized, Forbidden

from .schemas import (
    RegistrationRequestSchema,
    LoginRequestSchema,
    AuthResponseSchema,
    SuccessResponse,
    GetUserResponseSchema,
)
from . import api_bp


@api_bp.route("/register", methods=["POST"])
@api_bp.arguments(RegistrationRequestSchema)
@api_bp.response(201, AuthResponseSchema)
def register(data):

    if current_user.is_authenticated:
        raise Conflict("User is already registered")

    user = g.auth_service.register_user(data["username"], data["email"], data["password"])
    login_user(user, remember=False)
    return {"success": True, "data": user}


@api_bp.route("/login", methods=["POST"])
@api_bp.arguments(LoginRequestSchema)
@api_bp.response(200, AuthResponseSchema)
def login(data):

    if current_user.is_authenticated:
        raise Conflict("User is already logged in")
    user = g.auth_service.login(data["email"], data["password"])
    login_user(user, remember=False)
    return {"success": True, "data": user}


@api_bp.route("/logout", methods=["POST"])
@api_bp.response(200, SuccessResponse)
def logout():
    if not current_user.is_authenticated:
        raise Unauthorized("No user is currently logged in")
    logout_user()
    return {"success": True, "message": "User logged out"}


@api_bp.route("/user")
@api_bp.response(200, GetUserResponseSchema)
def get_user():
    if not current_user.is_authenticated:
        raise Unauthorized("No user is currently logged in")
    return {"success": True, "data": current_user}


@api_bp.route("/user/<int:user_id>")
@api_bp.response(200, GetUserResponseSchema)
def get_user_by_id(user_id: int):
    if not current_user.is_authenticated:
        raise Unauthorized("No user is currently logged in")
    if current_user.id != user_id and current_user.role != "admin":
        raise Forbidden("Cannot access another user's information")
    user = g.auth_service.get_user(user_id)
    return {"success": True, "data": user}


@api_bp.route("/user/<int:user_id>", methods=["DELETE"])
@login_required
@api_bp.response(200, SuccessResponse)
def delete_user(user_id: int):
    if current_user.id != user_id:
        raise Forbidden("Cannot delete another user's account")
    g.auth_service.delete_user(user_id)
    return {"success": True, "message": "User's Account Deleted"}

from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("")
def register_user():
    pass


@auth_bp.route("")
def login_user():
    pass


@auth_bp.route("")
def sign_out_user():
    pass


@auth_bp.route("")
def get_user(user_id: str):
    pass


@auth_bp.route("")
def change_password():
    pass


@auth_bp.route("")
def delete_user():
    pass

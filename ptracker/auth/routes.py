from flask import Blueprint, request, jsonify, g, render_template, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.exceptions import Conflict, Unauthorized, Forbidden

from ptracker.auth.forms import LoginForm, RegistrationForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# TODO: frontend show error messages from form validation and API responses


@auth_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("main.home_page"))

    form = LoginForm()

    if form.validate_on_submit():
        user = g.auth_service.login(form.email.data, form.password.data)
        login_user(user, remember=False)
        next_page = request.args.get("next")
        return redirect(next_page) if next_page else redirect(url_for("main.home_page"))

    return render_template("auth/login.html", title="Login", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for("main.home_page"))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = g.auth_service.register_user(form.username.data, form.email.data, form.password.data)
        login_user(user, remember=False)
        next_page = request.args.get("next")
        return redirect(next_page) if next_page else redirect(url_for("main.home_page"))
    return render_template("auth/register.html", title="Register", form=form)


@auth_bp.route("/forgot-password", methods=["GET"])
def forgot_password_page():
    if current_user.is_authenticated:
        raise Conflict("User is already logged in")
    return render_template("auth/forgot_password.html", title="Forgot Password")


@auth_bp.route("/logout")
def logout():
    if not current_user.is_authenticated:
        raise Unauthorized("No user is currently logged in")
    logout_user()
    return redirect(url_for("auth.login_page"))


@auth_bp.route("/api/register", methods=["POST"])
def register_api():

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


@auth_bp.route("/api/login", methods=["POST"])
def login_api():

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


@auth_bp.route("/api/logout", methods=["POST"])
def logout_api():
    if not current_user.is_authenticated:
        raise Unauthorized("No user is currently logged in")
    logout_user()
    return jsonify({"success": True, "message": "User logged out"}), 200


@auth_bp.route("/user/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id: int):
    if current_user.id != user_id:
        raise Forbidden("Cannot delete another user's account")
    g.auth_service.delete_user(user_id)
    return jsonify({"success": True, "message": "User's Account Deleted"}), 200


@auth_bp.route("/user/<int:user_id>/settings")
@login_required
def get_user_settings(user_id: int):
    if current_user.id != user_id:
        raise Forbidden("Cannot access another user's settings")
    # settings = g.auth_service.get_user_settings(user_id)
    # return jsonify({"success": True, "data": settings}), 200
    return render_template("auth/settings.html", title="Settings", settings=None, current_path=request.path)


@auth_bp.route("/demo", methods=["POST"])
def create_demo_session():
    if current_user.is_authenticated:
        raise Conflict("User is already logged in")
        # return jsonify({"success": False, "message": "Already logged in"}), 409
    user = g.auth_service.get_demo_user()
    login_user(user, remember=False)
    return jsonify({"success": True, "redirect": url_for("main.home_page")}), 200

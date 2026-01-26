from ptracker.models import User
from ptracker import db
from werkzeug.security import generate_password_hash, check_password_hash


class AuthService:

    def register_user(self, username: str, email: str, password: str):
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            raise ValueError("Username or email already exists")

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def authenticate_user(self, email: str, password: str):
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid credentials")
        return user

    def get_user(self, user_id: str):
        return User.query.get_or_404(user_id)

    # TODO Make sure the currently logged in user is changing their own credentials
    def change_password(self, user_id: int, new_password: str):
        user = User.query.get_or_404(user_id)
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

    def delete_user(self, user_id: int):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

from ptracker.models import User
from ptracker.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import NotFound


class AuthService:

    def register_user(self, username: str, email: str, password: str, role: str = "user") -> User:
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            raise ValueError("Username or email already exists")

        new_user = User(username=username, email=email, password_hash=generate_password_hash(password), role=role)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def login(self, email: str, password: str) -> User:
        user = self._authenticate_user(email, password)
        return user

    def _authenticate_user(self, email: str, password: str) -> User:
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid credentials")
        return user

    def get_user(self, user_id: str) -> User:
        user = db.session.get(User, user_id)
        if not user:
            raise NotFound("User not found")
        return user

    def change_password(self, user_id: int, new_password: str):
        user = db.session.get(User, user_id)
        if not user:
            raise NotFound("User not found")
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

    def delete_user(self, user_id: int):
        user = db.session.get(User, user_id)
        if not user:
            raise NotFound("User not found")
        db.session.delete(user)
        db.session.commit()

    def get_demo_user(self) -> User:
        demo_user = User.query.filter_by(email="demo@gmail.com").first()
        if not demo_user:
            demo_user = self.register_user("Demo User", "demo@gmail.com", "abc123", role="demo")
        return demo_user

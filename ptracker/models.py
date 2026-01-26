from sqlalchemy import UniqueConstraint
from ptracker.extensions import db
from datetime import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    tracked_items = db.relationship("UserItem", backref="user", lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(100), nullable=False)
    external_id = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)

    price_history = db.relationship("PriceHistory", backref="item", lazy=True)

    __table_args__ = (
        UniqueConstraint("vendor", "external_id", name="unique_vendor_external_id"),
    )

    def __repr__(self):
        return f"Item('{self.vendor}', '{self.url}', '{self.external_id}')"


class UserItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    target_price = db.Column(db.Float, nullable=False)

    item = db.relationship("Item", backref="user_items", lazy=True)

    __table_args__ = (
        db.UniqueConstraint("user_id", "item_id", name="unique_user_item"),
    )

    def __repr__(self):
        return f"UserItem(User ID: '{self.user_id}', Item ID: '{self.item_id}', Target Price: '{self.target_price}')"


class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Possible optimization for historical queires
    # __table_args__ = (
    #     db.Index("idx_price_history_item_time", "item_id", "timestamp"),
    # )

    def __repr__(self):
        return f"PriceHistory(Item ID: '{self.item_id}', Price: '{self.price}', Timestamp: '{self.timestamp}')"

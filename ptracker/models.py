from sqlalchemy import UniqueConstraint
from ptracker.extensions import db
from datetime import datetime, timezone
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(25), nullable=False, default="user")

    tracked_items = db.relationship("UserItem", backref="user", lazy=True)

    def __repr__(self):
        return f"<User id={self.id} username={self.username} role={self.role}>"


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(100), nullable=False)
    external_id = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)

    name = db.Column(db.String(255), nullable=True)
    currency = db.Column(db.String(10), nullable=True)
    current_price = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    in_stock = db.Column(db.Boolean, nullable=True)
    last_fetched = db.Column(db.DateTime, nullable=True)

    price_history = db.relationship("PriceHistory", backref="item", lazy=True)

    __table_args__ = (UniqueConstraint("vendor", "external_id", name="unique_vendor_external_id"),)

    def is_stale(self, max_age_hours: int = 1) -> bool:
        if not self.last_fetched:
            return True

        age_seconds = (datetime.now(timezone.utc) - self.last_fetched).total_seconds()
        return age_seconds > max_age_hours * 3600

    def __repr__(self):
        return f"<Item id={self.id} vendor={self.vendor}, external_id={self.external_id}>"


class UserItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    target_price = db.Column(db.Float, nullable=False)

    item = db.relationship("Item", backref="user_items", lazy=True)

    __table_args__ = (db.UniqueConstraint("user_id", "item_id", name="unique_user_item"),)

    def __repr__(self):
        return f"<UserItem id={self.id} user_id={self.user_id} item_id={self.item_id} target_price={self.target_price}>"


class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Possible optimization for historical queires
    # __table_args__ = (
    #     db.Index("idx_price_history_item_time", "item_id", "timestamp"),
    # )

    def __repr__(self):
        return f"<PriceHistory id={self.id} item_id={self.item_id} price={self.price} timestamp={self.timestamp}>"

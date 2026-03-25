from sqlalchemy import UniqueConstraint, Enum
from ptracker.extensions import db
from datetime import datetime, timezone
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(Enum("user", "demo", "admin", name="user_role"), nullable=False, default="user")
    notifications_enabled = db.Column(db.Boolean, default=True)

    tracked_items = db.relationship("UserItem", backref="user", lazy=True)

    def __repr__(self):
        return f"<User id={self.id} username={self.username} role={self.role}>"


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(100), nullable=False)
    external_id = db.Column(db.String(100), nullable=False)
    url = db.Column(db.Text, nullable=False)

    name = db.Column(db.String(500), nullable=True)
    currency = db.Column(db.String(10), nullable=True)
    current_price = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    in_stock = db.Column(db.Boolean, nullable=True)
    last_fetched = db.Column(db.DateTime, nullable=True)

    price_history = db.relationship("PriceHistory", backref="item", lazy=True)

    __table_args__ = (UniqueConstraint("vendor", "external_id", name="unique_vendor_external_id"),)

    def is_stale(self, max_age_hours: int = 24) -> bool:
        """Returns True if the item is stale and should be updated

        Stale if:
            - Never fetched before
            - Last fetch was more than `max_age_hours` ago
            - Last fetched was on a previous calendar day (UTC)

        Args:
            max_age_hours (int, optional): Expiration time of last fetched data. Defaults to 24.

        Returns:
            bool: _description_
        """
        if not self.last_fetched:
            return True

        # Ensure last_fetched is timezone-aware (SQLite returns naive datetimes)
        last_fetched_utc = (
            self.last_fetched.replace(tzinfo=timezone.utc) if self.last_fetched.tzinfo is None else self.last_fetched
        )
        now_utc = datetime.now(timezone.utc)
        age_seconds = (now_utc - last_fetched_utc).total_seconds()

        if age_seconds > max_age_hours * 3600 or last_fetched_utc.date() < now_utc.date():
            return True

        return False

    def __repr__(self):
        return f"<Item id={self.id} vendor={self.vendor}, external_id={self.external_id}>"


class UserItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"), nullable=False)
    target_price = db.Column(db.Float, nullable=False)
    notifications_enabled = db.Column(db.Boolean, default=True)

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

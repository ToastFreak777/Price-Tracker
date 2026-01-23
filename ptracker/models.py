from ptracker import db
from datetime import datetime


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"Item('{self.vendor}', '{self.url}')"


class User_items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    target_price = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "item_id", name="unique_user_item"),
    )

    def __repr__(self):
        return f"UserItem(User ID: '{self.user_id}', Item ID: '{self.item_id}', Target Price: '{self.target_price}')"


class Price_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)

    # Possible optimization for historical queires
    # db.index("idx_price_history_item_time", item_id, timestamp)

    def __repr__(self):
        return f"PriceHistory(Item ID: '{self.item_id}', Price: '{self.price}', Timestamp: '{self.timestamp}')"

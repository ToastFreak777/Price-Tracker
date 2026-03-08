from ptracker.datasources import DataSourceFactory, ProductSnapshot
from ptracker.models import User, Item, UserItem, PriceHistory
from ptracker.extensions import db
from werkzeug.exceptions import NotFound
from ptracker.notifications import EmailService

from datetime import datetime, timezone


class PriceTrackerService:

    def track_item(self, url: str, user_id: int, target_price: float) -> Item:
        vendor = DataSourceFactory.detect_vendor(url)
        source = DataSourceFactory.get(vendor)

        snapshot = source.fetch_from_url(url)

        item = Item.query.filter_by(vendor=vendor, external_id=snapshot.external_id).first()

        if not item:
            item = Item(
                vendor=vendor,
                url=url,
                external_id=snapshot.external_id,
                name=snapshot.name,
                currency=snapshot.currency,
                current_price=snapshot.price,
                image_url=snapshot.image_url,
                in_stock=snapshot.in_stock,
                last_fetched=snapshot.timestamp,
            )
            db.session.add(item)
            db.session.flush()

            price_record = PriceHistory(item_id=item.id, price=item.current_price)
            db.session.add(price_record)

        existing = UserItem.query.filter_by(user_id=user_id, item_id=item.id).first()
        if existing:
            raise ValueError("Item already tracked by user")

        user_item = UserItem(user_id=user_id, item_id=item.id, target_price=target_price)
        db.session.add(user_item)
        db.session.commit()

        return item

    def update_target_price(self, user_id: int, item_id: int, target_price: float):
        user_item = UserItem.query.filter_by(user_id=user_id, item_id=item_id).first()
        if not user_item:
            raise NotFound(f"No item with tracked with id: {item_id}")

        user_item.target_price = target_price
        db.session.commit()
        return user_item

    def _fetch_live_snapshot(self, item: Item) -> ProductSnapshot:
        source = DataSourceFactory.get(item.vendor)
        return source.fetch_from_url(item.url)

    def get_item(self, item_id: int):
        item = db.session.get(Item, item_id)
        if not item:
            raise NotFound(f"No item with id: {item_id}")

        history = PriceHistory.query.filter_by(item_id=item_id).order_by(PriceHistory.timestamp.desc()).all()

        return {
            "item": item,
            "price_history": history,
        }

    def remove_item(self, user_id: int, item_id: int):
        user_item = UserItem.query.filter_by(user_id=user_id, item_id=item_id).first()
        if not user_item:
            raise NotFound("Item not found in user's tracked list")

        db.session.delete(user_item)
        db.session.commit()

    def _update_item_price(self, item: Item):
        """Core logic for fetching and updating item price once per day.

        Fetches if stale (24+ hours since last fetch) and records unrecorded price changes.
        Always adds a daily price history snapshot for tracking.
        Commits changes.
        """
        if item.is_stale(max_age_hours=24):
            snapshot = self._fetch_live_snapshot(item)
            item.name = snapshot.name
            item.image_url = snapshot.image_url
            item.currency = snapshot.currency
            item.current_price = snapshot.price
            item.in_stock = snapshot.in_stock
            item.last_fetched = datetime.now(timezone.utc)

            db.session.add(PriceHistory(item_id=item.id, price=snapshot.price))
            db.session.commit()

    def check_price_and_update(self, item_id: int):
        """Public method to check and update price by item_id."""
        item = db.session.get(Item, item_id)
        if not item:
            raise NotFound(f"No item with id: {item_id}")

        self._update_item_price(item)

    def calculate_price_change(self, item: Item) -> float:
        prev_price = (
            PriceHistory.query.filter_by(item_id=item.id).order_by(PriceHistory.timestamp.desc()).offset(1).first()
        )
        if not prev_price or not prev_price.price:
            return 0.0

        return round(((item.current_price - prev_price.price) / prev_price.price) * 100, 2)

    def check_price_change_and_notify_all(self):
        self.update_all_tracked_items()
        user_items = UserItem.query.join(Item).all()

        for ui in user_items:
            item = ui.item
            price_change = self.calculate_price_change(item)

            if (
                ui.user.notifications_enabled
                and ui.notifications_enabled
                and price_change < 0
                and item.current_price <= ui.target_price
            ):
                email_service = EmailService()
                email_service.send_email(ui.user.email)

    def get_user_tracked_items(self, user_id: int):
        """Get user's tracked items with full details, optionally refreshing stale data"""
        user = db.session.get(User, user_id)
        if not user:
            raise NotFound(f"No user with id: {user_id}")

        result = []
        for user_item in user.tracked_items:
            price_change = self.calculate_price_change(user_item.item)

            result.append(
                {
                    "item": user_item.item,
                    "target_price": user_item.target_price,
                    "current_price": user_item.item.current_price,
                    "price_change": price_change,
                    "notifications_enabled": user_item.notifications_enabled,
                }
            )

        return result

    def get_user_item(self, user_id: int, item_id: int):
        user_item = db.session.query(UserItem).filter_by(user_id=user_id, item_id=item_id).first()
        if not user_item:
            raise NotFound("Item not found in user's tracked list")

        price_change = self.calculate_price_change(user_item.item)

        return {
            "item": user_item.item,
            "target_price": user_item.target_price,
            "price_change": price_change,
        }

    def update_item_target_price(self, user_id: int, item_id: int, target_price: float):
        user_item = db.session.query(UserItem).filter_by(user_id=user_id, item_id=item_id).first()
        if not user_item:
            raise NotFound("Item not found in user's tracked list")

        user_item.target_price = target_price
        db.session.commit()

    def update_all_tracked_items(self):
        """Utility method to update all tracked items.
        In production, this would be run as a scheduled background job.
        """
        items = db.session.query(Item).join(UserItem).distinct().all()
        for item in items:
            try:
                self._update_item_price(item)
            except Exception as e:
                print(f"Error updating item {item.id}: {e}")

    def update_user_notifications(self, user_id: int, enabled: bool):
        user = db.session.get(User, user_id)
        if not user:
            raise NotFound(f"No user with id: {user_id}")

        user.notifications_enabled = enabled
        db.session.commit()

    def update_item_notifications(self, user_id: int, item_id: int, enabled: bool):
        user_item = db.session.query(UserItem).filter_by(user_id=user_id, item_id=item_id).first()
        if not user_item:
            raise NotFound("Item not found in user's tracked list")

        user_item.notifications_enabled = enabled
        db.session.commit()

from ptracker.datasources import DataSourceFactory, ProductSnapshot
from ptracker.models import User, Item, UserItem, PriceHistory
from ptracker.extensions import db
from werkzeug.exceptions import NotFound


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

    def _update_item_cache(self, item: Item, snapshot: ProductSnapshot):
        from datetime import datetime, timezone

        item.name = snapshot.name
        item.image_url = snapshot.image_url
        item.currency = snapshot.currency
        item.current_price = snapshot.price
        item.in_stock = snapshot.in_stock
        item.last_fetched = datetime.now(timezone.utc)

    def get_item(self, item_id: int):
        item = db.session.get(Item, item_id)
        if not item:
            raise NotFound(f"No item with id: {item_id}")

        # Only fetch live data if cache is stale
        if item.is_stale(max_age_hours=1):
            snapshot = self._fetch_live_snapshot(item)
            old_price = item.current_price
            self._update_item_cache(item, snapshot)

            if old_price != snapshot.price:
                db.session.add(PriceHistory(item_id=item.id, price=snapshot.price))

            db.session.commit()

        history = PriceHistory.query.filter_by(item_id=item_id).order_by(PriceHistory.timestamp.desc()).all()

        return {
            "item": item,
            "price_history": history,
        }

    def get_items(self, user_id: int) -> list[UserItem]:
        user = db.session.get(User, user_id)
        if not user:
            raise NotFound(f"No user with id: {user_id}")
        return user.tracked_items

    def remove_item(self, user_id: int, item_id: int):
        user_item = UserItem.query.filter_by(user_id=user_id, item_id=item_id).first()
        if not user_item:
            raise NotFound("Item not found in user's tracked list")

        db.session.delete(user_item)
        db.session.commit()

    def check_price_update(self, item_id: int):
        item = db.session.get(Item, item_id)
        if not item:
            raise NotFound(f"No item with id: {item_id}")

        snapshot = self._fetch_live_snapshot(item)
        old_price = item.current_price
        self._update_item_cache(item, snapshot)

        if old_price != snapshot.price:
            db.session.add(PriceHistory(item_id=item.id, price=snapshot.price))

        db.session.commit()

    def get_user_tracked_items(self, user_id: int, refresh_stale: bool = True):
        """Get user's tracked items with full details, optionally refreshing stale data"""
        user = db.session.get(User, user_id)
        if not user:
            raise NotFound(f"No user with id: {user_id}")

        result = []
        for user_item in user.tracked_items:
            item = user_item.item

            # Refresh stale data if requested
            if refresh_stale and item.is_stale(max_age_hours=1):
                try:
                    snapshot = self._fetch_live_snapshot(item)
                    old_price = item.current_price
                    self._update_item_cache(item, snapshot)

                    # Update price history if price changed
                    if old_price != snapshot.price:
                        db.session.add(PriceHistory(item_id=item.id, price=snapshot.price))

                    db.session.commit()
                except Exception as e:
                    # Log error but don't fail entire request
                    print(f"Error refreshing item {item.id}: {e}")

            price_drop = None
            if item.current_price and user_item.target_price:
                price_drop = ((user_item.target_price - item.current_price) / user_item.target_price) * 100

            result.append(
                {
                    "item": item,
                    "user_item": user_item,
                    "current_price": item.current_price,
                    "price_drop": price_drop,
                }
            )

        return result

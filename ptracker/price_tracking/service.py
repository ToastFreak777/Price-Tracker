from ptracker.datasources import DataSourceFactory, ProductSnapshot
from ptracker.models import User, Item, UserItem, PriceHistory
from ptracker.extensions import db


class PriceTrackerService:

    def track_item(self, url: str, user_id: int, target_price: float) -> Item:
        vendor = DataSourceFactory.detect_vendor(url)
        source = DataSourceFactory.get(vendor)

        snapshot = source.fetch_from_url(url)

        item = Item.query.filter_by(
            vendor=vendor, external_id=snapshot.external_id
        ).first()

        if not item:
            item = Item(vendor=vendor, url=url, external_id=snapshot.external_id)
            db.session.add(item)
            db.session.flush()

            price_record = PriceHistory(
                item_id=item.id,
                price=snapshot.price,
            )
            db.session.add(price_record)

        existing = UserItem.query.filter_by(user_id=user_id, item_id=item.id).first()
        if existing:
            raise ValueError("Item already tracked by user")

        user_item = UserItem(
            user_id=user_id, item_id=item.id, target_price=target_price
        )
        db.session.add(user_item)
        db.session.commit()

        return item

    def update_target_price(self, user_id: int, item_id: int, target_price: float):
        user_item = UserItem.query.filter_by(
            user_id=user_id, item_id=item_id
        ).first_or_404(f"No item with tracked with id: {item_id}")

        user_item.target_price = target_price
        db.session.commit()
        return user_item

    def _fetch_live_snapshot(self, item: Item) -> ProductSnapshot:
        source = DataSourceFactory.get(item.vendor)
        return source.fetch_from_url(item.url)

    def get_item(self, item_id: int):
        item = Item.query.get_or_404(item_id, f"No item with id: {item_id}")

        snapshot = self._fetch_live_snapshot(item)

        history = (
            PriceHistory.query.filter_by(item_id=item_id)
            .order_by(PriceHistory.timestamp.desc())
            .all()
        )

        return {
            "item": item,
            "snapshot": snapshot,
            "price_history": history,
        }

    def get_items(self, user_id: int) -> list[UserItem]:
        user = User.query.get_or_404(user_id, f"No user with id: {user_id}")
        return user.tracked_items

    def remove_item(self, user_id: int, item_id: int):
        user_item = UserItem.query.filter_by(
            user_id=user_id, item_id=item_id
        ).first_or_404("Item not found in user's tracked list")

        db.session.delete(user_item)
        db.session.commit()

    def check_price_update(self, item_id: int) -> bool:
        item = Item.query.get(item_id)
        if not item:
            return False

        snapshot = self._fetch_live_snapshot(item)

        last_price = (
            PriceHistory.query.filter_by(item_id=item_id)
            .order_by(PriceHistory.timestamp.desc())
            .first()
        )

        if not last_price or last_price.price != snapshot.price:
            db.session.add(PriceHistory(item_id=item.id, price=snapshot.price))
            db.session.commit()
            return True

        return False

from ptracker.datasources import DataSourceFactory, ProductSnapshot
from ptracker.models import Item, PriceHistory
from ptracker import db


class PriceTrackerService:

    def add_item(self, url: str, user_id: int, target_price: float):
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
        db.session.commit()

        return item

    def _fetch_live_snapshot(self, item: Item) -> ProductSnapshot:
        source = DataSourceFactory.get(item.vendor)
        return source.fetch_from_url(item.url)

    def get_item(self, item_id: int):
        item = Item.query.get_or_404(item_id)

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

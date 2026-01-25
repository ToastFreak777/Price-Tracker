from ptracker.datasources import DataSourceFactory, ProductSnapshot
from ptracker.models import Item, PriceHistory
from ptracker import db


class PriceTrackerService:

    def add_item(self, url: str, user_id: int, target_price: float):
        vendor = DataSourceFactory.detect_vendor(url)
        source = DataSourceFactory.get(vendor)

        snapshot = source.fetch_product(url)

        item = Item(vendor=vendor, url=url)
        db.session.add(item)
        db.session.flush()

        price_record = PriceHistory(
            item_id=item.id,
            price=snapshot.price,
        )
        db.session.add(price_record)
        db.session.commit()

        return item

    def check_price_update(self, item_id: int) -> bool:
        item = Item.query.get(item_id)
        source = DataSourceFactory.get(item.vendor)

        # Fetch current price
        snapshot = source.fetch_product(item.url)

        last_price = (
            PriceHistory.query.filter_by(item_id=item_id)
            .order_by(PriceHistory.timestamp.desc())
            .first()
        )

        if last_price.price != snapshot.price:
            new_record = PriceHistory(item_id=item_id, price=snapshot.price)
            db.session.add(new_record)
            db.session.commit()
            return True

        return False

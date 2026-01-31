from ptracker.datasources.base import ProductSnapshot
from ptracker.price_tracking.service import PriceTrackerService
from ptracker.models import Item, PriceHistory, UserItem
from ptracker.extensions import db
import pytest


def test_track_item_returns_correct_data(auth_client):
    service = PriceTrackerService()

    item = service.track_item("https://mock.com/items/123", 1, 700)

    assert item.url == "https://mock.com/items/123"
    assert item.vendor == "mock"

    user_item = UserItem.query.filter_by(user_id=1, item_id=item.id).first()

    assert user_item is not None
    assert user_item.target_price == 700
    assert user_item.user_id == 1 and user_item.item_id == item.id

    price_record = PriceHistory.query.filter_by(item_id=item.id).first()
    assert price_record is not None


def test_track_item_raises_on_duplicate(auth_client):
    service = PriceTrackerService()

    # Track initial item
    service.track_item("https://mock.com/items/123", 1, 700)

    with pytest.raises(ValueError, match="Item already tracked by user"):
        # Attempt to track same item
        service.track_item("https://mock.com/items/123", 1, 600)


def test_update_target_price_updates_correctly(auth_client):
    service = PriceTrackerService()

    # Track item
    item = service.track_item("https://mock.com/items/123", 1, 700)
    user_item = service.update_target_price(1, item.id, 500)

    assert user_item.target_price == 500


def test_get_item_returns_correct_data(auth_client):
    service = PriceTrackerService()

    # Add item to track
    service.track_item("https://mock.com/items/123", 1, 700)

    result = service.get_item(1)
    assert "item" in result
    assert "snapshot" in result
    assert "price_history" in result
    assert isinstance(result["price_history"], list)


def test_check_price_update_changes_price(app, mocker):
    with app.app_context():
        # Setup item + price history
        item = Item(vendor="mock", external_id="123", url="https://mock.com/items/123")
        db.session.add(item)
        db.session.flush()
        history = PriceHistory(item_id=item.id, price=100.0)
        db.session.add(history)
        db.session.commit()

        # Mock datasource fetch to return different price
        mock_source = mocker.MagicMock()
        mock_source.fetch_from_url.return_value = ProductSnapshot(
            vendor="mock",
            external_id="123",
            name="Mock Product",
            price=150.0,
            currency="USD",
            in_stock=True,
            url="https://mock.com/items/123",
        )
        mocker.patch(
            "ptracker.price_tracking.service.DataSourceFactory.get",
            return_value=mock_source,
        )
        mocker.patch(
            "ptracker.price_tracking.service.DataSourceFactory.detect_vendor",
            return_value="mock",
        )

        service = PriceTrackerService()
        result = service.check_price_update(item.id)
        assert PriceHistory.query.filter_by(item_id=item.id).count() == 2

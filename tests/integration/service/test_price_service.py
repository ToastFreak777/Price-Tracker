import pytest
from datetime import datetime, timezone
from ptracker.datasources.base import ProductSnapshot
from ptracker.price_tracking.service import PriceTrackerService
from ptracker.models import Item, PriceHistory, UserItem
from ptracker.extensions import db


def test_track_item_success(app):
    service = PriceTrackerService()

    # Mock Item has a base price of 99.99
    expected = {
        "vendor": "mock",
        "url": "https://mock.com/items/123",
        "user_id": 1,
        "target_price": 700,
    }

    item = service.track_item(expected["url"], expected["user_id"], expected["target_price"])

    assert item.url == expected["url"]
    assert item.vendor == expected["vendor"]

    user_item = UserItem.query.filter_by(user_id=expected["user_id"], item_id=item.id).first()

    assert user_item is not None
    assert user_item.target_price == expected["target_price"]
    assert user_item.user_id == expected["user_id"] and user_item.item_id == item.id

    price_record = PriceHistory.query.filter_by(item_id=item.id).first()
    assert price_record is not None
    assert price_record.price == item.current_price


def test__update_item_price_stale(item_no_history, mocker):
    service = PriceTrackerService()

    fake_snapshot = ProductSnapshot(
        vendor=item_no_history.vendor,
        external_id=item_no_history.external_id,
        name=item_no_history.name,
        price=49.99,
        currency=item_no_history.currency,
        in_stock=item_no_history.in_stock,
        url=item_no_history.url,
        image_url=item_no_history.image_url,
        timestamp=datetime.now(timezone.utc),
    )
    fetch_mock = mocker.patch.object(
        PriceTrackerService,
        "_fetch_live_snapshot",
        return_value=fake_snapshot,
    )

    before_count = PriceHistory.query.filter_by(item_id=item_no_history.id).count()
    service._update_item_price(item_no_history)

    fetch_mock.assert_called_once_with(item_no_history)
    assert item_no_history.current_price == fake_snapshot.price
    assert item_no_history.name == fake_snapshot.name
    assert item_no_history.currency == fake_snapshot.currency
    assert item_no_history.in_stock == fake_snapshot.in_stock
    assert item_no_history.image_url == fake_snapshot.image_url
    assert item_no_history.last_fetched is not None
    assert PriceHistory.query.filter_by(item_id=item_no_history.id).count() == before_count + 1


def test__update_item_price_not_stale(item_no_history, mocker):
    service = PriceTrackerService()

    mocker.patch.object(
        PriceTrackerService,
        "_fetch_live_snapshot",
        return_value=ProductSnapshot(
            vendor=item_no_history.vendor,
            external_id=item_no_history.external_id,
            name=item_no_history.name,
            price=49.99,
            currency=item_no_history.currency,
            in_stock=item_no_history.in_stock,
            url=item_no_history.url,
            timestamp=datetime.now(timezone.utc),
        ),
    )
    service._update_item_price(item_no_history)

    # Second call shoud not fetch
    fetch_mock = mocker.patch.object(PriceTrackerService, "_fetch_live_snapshot")
    service._update_item_price(item_no_history)
    fetch_mock.assert_not_called()


def test_track_item_raises_on_duplicate(app):
    service = PriceTrackerService()

    url = "https://mock.com/items/123"
    user_id = 1

    # Track initial item
    item = service.track_item(url, user_id, 700)

    with pytest.raises(ValueError, match="Item already tracked by user"):
        # Attempt to track same item
        service.track_item(item.url, user_id, 600)


def test_check_price_and_update_success(item_no_history, mocker):
    # Mock datasource fetch to return different price
    mock_source = mocker.MagicMock()
    mock_source.fetch_from_url.return_value = ProductSnapshot(
        vendor=item_no_history.vendor,
        external_id=item_no_history.external_id,
        name=item_no_history.name,
        price=499.99,
        currency=item_no_history.currency,
        in_stock=item_no_history.in_stock,
        url=item_no_history.url,
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
    service.check_price_and_update(item_no_history.id)
    assert PriceHistory.query.filter_by(item_id=item_no_history.id).count() == 2


def test_calculate_price_change(item_with_history):
    # Item has price history of 100 -> 90, so change should be -10%
    service = PriceTrackerService()
    change_pct = service.calculate_price_change(item_with_history)
    assert change_pct == -10.0  # From 100 to 90 is a 10% decrease


def test_calculate_price_change_no_previous_price(item_no_history):
    service = PriceTrackerService()
    change_pct = service.calculate_price_change(item_no_history)
    assert change_pct == 0.0  # No previous price to compare to


def test_check_price_change_and_notify_all_sends_email(app, auth_user, mocker):
    service = PriceTrackerService()

    mocker.patch.object(service, "update_all_tracked_items")

    send_email_mock = mocker.patch("ptracker.price_tracking.service.EmailService.send_email")

    # Create item and add to DB
    item = Item(vendor="mock", external_id="123", url="https://mock.com/items/123", current_price=49.99)
    db.session.add(item)
    db.session.flush()

    user_item = UserItem(user_id=auth_user.id, item_id=item.id, target_price=50.0)
    db.session.add(user_item)
    db.session.flush()

    # Simulate price drop by adding prev price above target
    prev_history = PriceHistory(item_id=item.id, price=55.0)
    db.session.add(prev_history)
    db.session.flush()

    latest_history = PriceHistory(item_id=item.id, price=item.current_price)
    db.session.add(latest_history)
    db.session.commit()

    service.check_price_change_and_notify_all()
    send_email_mock.assert_called_once_with(auth_user.email)


@pytest.mark.parametrize(
    "user_notifications, item_notifications, price_change, current_price",
    [
        (False, True, -5.0, 49.99),
        (True, False, -5.0, 49.99),
        (True, True, 5.0, 49.99),
        (True, True, -5.0, 150.00),
    ],
    ids=[
        "user_notifications_disabled",
        "item_notifications_disabled",
        "price_increased",
        "price_dropped_above_target",
    ],
)
def test_check_price_change_and_notify_all_fails(
    app, auth_user, mocker, user_notifications, item_notifications, price_change, current_price
):
    service = PriceTrackerService()

    mocker.patch.object(service, "update_all_tracked_items")
    # Simulate price drop
    mocker.patch.object(service, "calculate_price_change", return_value=price_change)

    send_email_mock = mocker.patch("ptracker.price_tracking.service.EmailService.send_email")

    auth_user.notifications_enabled = user_notifications

    item = Item(
        vendor="mock",
        external_id="123",
        url="https://mock.com/items/123",
        current_price=current_price,
    )
    db.session.add(item)
    db.session.flush()
    user_item = UserItem(
        user_id=auth_user.id,
        item_id=item.id,
        target_price=50.0,
        notifications_enabled=item_notifications,
    )
    db.session.add(user_item)
    db.session.commit()

    service.check_price_change_and_notify_all()
    send_email_mock.assert_not_called()

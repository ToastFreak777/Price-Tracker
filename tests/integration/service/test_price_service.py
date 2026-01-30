from ptracker.price_tracking.service import PriceTrackerService
from ptracker.models import UserItem
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

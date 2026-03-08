from flask import request, g
from flask_login import current_user, login_required

from .schemas import (
    GetItemResponseSchema,
    SuccessResponse,
    TrackItemRequest,
    TrackItemResponse,
    GetUserItemsResponseSchema,
)

from . import api_bp


@api_bp.route("/items/<int:item_id>")
@api_bp.response(200, GetItemResponseSchema)
@login_required
def get_item(item_id):
    result = g.price_service.get_item(item_id)

    item = result["item"]
    item.price_history = result["price_history"]
    return {"data": item}


@api_bp.route("/items")
@api_bp.response(200, GetUserItemsResponseSchema)
@login_required
def get_items():
    result = g.price_service.get_user_tracked_items(current_user.id)
    return {"data": result}


@api_bp.route("/items/add", methods=["POST"])
@api_bp.arguments(TrackItemRequest)
@api_bp.response(201, TrackItemResponse)
@login_required
def track_item(data):
    item = g.price_service.track_item(data["url"], current_user.id, data["target_price"])
    return {"data": item}


@api_bp.route("/items/<int:item_id>", methods=["DELETE"])
@api_bp.response(200, SuccessResponse)
@login_required
def untrack_item(item_id):
    g.price_service.remove_item(current_user.id, item_id)
    return {"success": True, "message": f"Item {item_id} untracked"}


@api_bp.route("/update-items")
@api_bp.response(200, SuccessResponse)
def update_all_items():
    """Endpoint to trigger manual update of all tracked items.
    In production, this would be handled by a scheduled background job.
    """
    g.price_service.check_price_change_and_notify_all()
    return {"success": True, "message": "All items updated"}


@api_bp.route("/user/notifications", methods=["PATCH"])
@api_bp.response(200, SuccessResponse)
@login_required
def update_user_notifications():
    data = request.get_json()
    g.price_service.update_user_notifications(current_user.id, data.get("enabled", True))
    return {"success": True, "message": "user notifications updated"}


@api_bp.route("/items/<int:item_id>/notifications", methods=["PATCH"])
@api_bp.response(200, SuccessResponse)
@login_required
def update_item_notifications(item_id):
    data = request.get_json()
    g.price_service.update_item_notifications(current_user.id, item_id, data.get("enabled", True))
    return {"success": True, "message": "item notifications updated"}

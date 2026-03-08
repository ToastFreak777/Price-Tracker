from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Email()


class PriceHistory(Schema):
    id = fields.Int()
    item_id = fields.Int()
    price = fields.Float()
    timestamp = fields.DateTime()


class ItemSchema(Schema):
    id = fields.Int()
    vendor = fields.Str()
    external_id = fields.Str()
    url = fields.Str()
    name = fields.Str()
    currency = fields.Str()
    current_price = fields.Float()
    image_url = fields.Str()
    in_stock = fields.Bool()
    last_fetched = fields.DateTime()

    price_history = fields.List(fields.Nested("PriceHistory"))


class UserItemSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    item_id = fields.Int()
    target_price = fields.Float()
    notifications_enabled = fields.Bool()
    item = fields.Nested("ItemSchema")


class UserProfileSchema(UserSchema):
    role = fields.Str()
    notifications_enabled = fields.Bool()
    tracked_items = fields.List(fields.Nested("UserItemSchema"))


class SuccessResponse(Schema):
    success = fields.Constant(True)
    message = fields.Str(metadata={"description": "A short success message", "example": "Operation successful"})


class AuthResponseSchema(Schema):
    success = fields.Constant(True)
    data = fields.Nested("UserSchema")


class LoginRequestSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class RegistrationRequestSchema(LoginRequestSchema):
    username = fields.Str(required=True)


class GetUserResponseSchema(Schema):
    success = fields.Constant(True)
    data = fields.Nested("UserProfileSchema")


class GetItemResponseSchema(Schema):
    success = fields.Constant(True)
    data = fields.Nested("ItemSchema")


class TrackItemRequest(Schema):
    url = fields.Str(required=True)
    target_price = fields.Float(required=True)


class TrackItemResponse(Schema):
    success = fields.Constant(True)
    data = fields.Nested("ItemSchema")


class UserTrackedItemsSchema(Schema):
    item = fields.Nested("ItemSchema")
    target_price = fields.Float()
    current_price = fields.Float()
    price_change = fields.Float()
    notifications_enabled = fields.Bool()


class GetUserItemsResponseSchema(Schema):
    success = fields.Constant(True)
    data = fields.Nested("UserTrackedItemsSchema", many=True)

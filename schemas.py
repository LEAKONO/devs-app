from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    role = fields.Str(dump_only=True)

class SellerSchema(Schema):
    id = fields.Int(dump_only=True)
    user = fields.Nested(UserSchema)
    is_approved = fields.Bool(dump_only=True)

class ComplaintSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    description = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)

class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    seller_id = fields.Int(required=True)

class OrderSchema(Schema):
    id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    user_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)

class CartSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)

class FeedbackSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    product_id = fields.Int(required=True)
    rating = fields.Int(required=True)
    comment = fields.Str()
    created_at = fields.DateTime(dump_only=True)

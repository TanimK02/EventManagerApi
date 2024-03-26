from marshmallow import Schema, fields


class PlannerSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True)
    name = fields.Str(required=True)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True)
    name = fields.Str(required=True)

class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    creator = fields.Str(dump_only=True)
    creator_id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    price = fields.Int(required=False)
    max_attendants = fields.Int(required=False)
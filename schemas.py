from marshmallow import Schema, fields


class PlannerSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True)
    name = fields.Str(required=True)

class ItterPlannerSchema(Schema):
    username = fields.Str(dump_only=True)
    email = fields.Str(dump_only=True)
    name = fields.Str(dump_only=True)

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
    date = fields.Date(required=False)
    description = fields.Str(required=True)
    price = fields.Int(required=False)
    max_attendants = fields.Int(required=False)
    attendants = fields.Int(dump_only=True)
    editors = fields.List(fields.Nested(ItterPlannerSchema()), dump_only=True)
    status = fields.Str(required=False)
    created_at = fields.Date(dump_only=True)
    updated_at = fields.Date(dump_only=True)
    published_at = fields.Date(dump_only=True)
    rating = fields.Int(dump_only=True)
    

class EventSchema_Editors(Schema):
    id = fields.Int(dump_only=True)
    creator = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    date = fields.Date(required=False)
    description = fields.Str(required=True)
    price = fields.Int(required=False)
    max_attendants = fields.Int(required=False)
    attendants = fields.Int(dump_only=True)
    editors = fields.List(fields.Nested(ItterPlannerSchema()), dump_only=True)
    status = fields.Str(required=False)
    created_at = fields.Date(dump_only=True)
    updated_at = fields.Date(dump_only=True)
    published_at = fields.Date(dump_only=True)
    rating = fields.Int(dump_only=True)


class EventResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    creator = fields.Str(dump_only=True)
    title = fields.Str(dump_only=True)
    description = fields.Str(dump_only=True)
    date = fields.Date(dump_only=True)
    price = fields.Float(dump_only=True)
    max_attendants = fields.Int(dump_only=True)
    attendants = fields.Int(dump_only=True)
    updated_at = fields.Date(dump_only=True)
    published_at = fields.Date(dump_only=True)
    rating = fields.Int(dump_only=True)
    status = fields.Str(dump_only=True)


class EventEditSchema(Schema):
    id = fields.Int(dump_only=True)
    creator = fields.Str(dump_only=True)
    creator_id = fields.Int(dump_only=True)
    title = fields.Str(required=False)  
    date = fields.Date(required=False)
    description = fields.Str(required=False)  
    price = fields.Int(required=False)
    max_attendants = fields.Int(required=False)
    attendants = fields.Int(dump_only=True)
    editors = fields.List(fields.Nested(ItterPlannerSchema()), dump_only=True)
    status = fields.Str(required=False)
    created_at = fields.Date(dump_only=True)
    updated_at = fields.Date(dump_only=True)
    published_at = fields.Date(dump_only=True)
    rating = fields.Int(dump_only=True)


class EditorSchema(Schema):
    editors = fields.List(fields.Str(required=True))


class ReviewSchema(Schema):
    id = fields.Int(dump_only=True)
    rate = fields.Int(required=True)
    comment = fields.Str(required=True)
    created_at = fields.Date(dump_only=True)
    updated_at = fields.Date(dump_only=True)

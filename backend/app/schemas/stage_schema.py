from marshmallow import Schema, fields, validate


class CreateStageSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    position = fields.Integer(load_default=0)

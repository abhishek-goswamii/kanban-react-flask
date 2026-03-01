from marshmallow import Schema, fields, validate


class CreateCommentSchema(Schema):
    content = fields.String(required=True, validate=validate.Length(min=1, max=5000))

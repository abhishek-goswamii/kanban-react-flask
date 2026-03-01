from marshmallow import Schema, fields, validate


class CreateProjectSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    description = fields.String(validate=validate.Length(max=1000), load_default="")


class UpdateProjectSchema(Schema):
    name = fields.String(validate=validate.Length(min=1, max=255))
    description = fields.String(validate=validate.Length(max=1000))

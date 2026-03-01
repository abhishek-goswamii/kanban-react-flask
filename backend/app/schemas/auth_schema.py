from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=255))
    password = fields.String(required=True, validate=validate.Length(min=6, max=128))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

from marshmallow import Schema, fields, validate
from app.core.constants import ProjectRole


class InviteMemberSchema(Schema):
    email = fields.Email(required=True)
    role = fields.String(
        validate=validate.OneOf(ProjectRole.ALL),
        load_default=ProjectRole.MEMBER,
    )

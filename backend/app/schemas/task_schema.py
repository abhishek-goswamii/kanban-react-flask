from marshmallow import Schema, fields, validate


class CreateTaskSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    description = fields.String(validate=validate.Length(max=5000), load_default="")
    stage_id = fields.Integer(required=True)
    assignee_id = fields.Integer(load_default=None, allow_none=True)


class UpdateTaskSchema(Schema):
    title = fields.String(validate=validate.Length(min=1, max=255))
    description = fields.String(validate=validate.Length(max=5000))
    assignee_id = fields.Integer(allow_none=True)


class MoveTaskSchema(Schema):
    stage_id = fields.Integer(required=True)
    position = fields.Integer(required=True)

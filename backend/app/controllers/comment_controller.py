from flask import Blueprint, request
from marshmallow import ValidationError

from app.core.constants import Messages
from app.core.response import APIResponse
from app.core.database import SessionLocal
from app.middleware.auth_middleware import auth_required
from app.services.comment_service import CommentService
from app.schemas.comment_schema import CreateCommentSchema

comment_bp = Blueprint("comments", __name__)


@comment_bp.route("", methods=["POST"])
@auth_required
def create_comment(current_user):
    """add a comment to a task"""
    schema = CreateCommentSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors=err.messages, code=400)

    task_id = request.args.get("task_id", type=int)
    if not task_id:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors={"task_id": ["required"]}, code=400)

    db = SessionLocal()
    try:
        service = CommentService(db)
        comment, error = service.add_comment(
            task_id=task_id,
            content=data["content"],
            author_id=current_user.id,
        )
        if error:
            code = 404 if error == Messages.TASK_NOT_FOUND else 403
            return APIResponse.error(message=error, code=code)

        return APIResponse.success(data=comment.to_dict(), message=Messages.COMMENT_CREATED, code=201)
    except Exception as e:
        db.rollback()
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()


@comment_bp.route("", methods=["GET"])
@auth_required
def get_comments(current_user):
    """get all comments for a task"""
    task_id = request.args.get("task_id", type=int)
    if not task_id:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors={"task_id": ["required"]}, code=400)

    db = SessionLocal()
    try:
        service = CommentService(db)
        comments, error = service.get_comments(task_id, current_user.id)
        if error:
            code = 404 if error == Messages.TASK_NOT_FOUND else 403
            return APIResponse.error(message=error, code=code)

        return APIResponse.success(data=comments)
    except Exception as e:
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()


@comment_bp.route("/<int:comment_id>", methods=["DELETE"])
@auth_required
def delete_comment(current_user, comment_id):
    """delete a comment"""
    db = SessionLocal()
    try:
        service = CommentService(db)
        error = service.delete_comment(comment_id, current_user.id)
        if error:
            code = 404 if error == Messages.COMMENT_NOT_FOUND else 403
            return APIResponse.error(message=error, code=code)

        return APIResponse.success(message=Messages.COMMENT_DELETED)
    except Exception as e:
        db.rollback()
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()

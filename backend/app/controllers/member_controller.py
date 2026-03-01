from flask import Blueprint, request
from marshmallow import ValidationError

from app.core.constants import Messages
from app.core.response import APIResponse
from app.core.database import SessionLocal
from app.middleware.auth_middleware import auth_required
from app.services.member_service import MemberService
from app.schemas.member_schema import InviteMemberSchema

member_bp = Blueprint("members", __name__)


@member_bp.route("/add", methods=["POST"])
@auth_required
def add_member(current_user):
    """directly add a user to a project"""
    schema = InviteMemberSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors=err.messages, code=400)

    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors={"project_id": ["required"]}, code=400)

    db = SessionLocal()
    try:
        service = MemberService(db)
        member, error = service.add_member(
            project_id=project_id,
            email=data["email"],
            role=data["role"],
            adder_id=current_user.id,
        )
        if error:
            code = 404 if error == Messages.USER_NOT_FOUND else 409 if error == Messages.ALREADY_A_MEMBER else 403
            return APIResponse.error(message=error, code=code)

        return APIResponse.success(data=member.to_dict(), message=Messages.MEMBER_ADDED, code=201)
    except Exception as e:
        db.rollback()
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()


@member_bp.route("", methods=["GET"])
@auth_required
def get_members(current_user):
    """get all members of a project"""
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors={"project_id": ["required"]}, code=400)

    db = SessionLocal()
    try:
        service = MemberService(db)
        members, error = service.get_members(project_id, current_user.id)
        if error:
            return APIResponse.error(message=error, code=403)

        return APIResponse.success(data=members)
    except Exception as e:
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()




@member_bp.route("/<int:member_user_id>", methods=["DELETE"])
@auth_required
def remove_member(current_user, member_user_id):
    """remove a member from a project"""
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors={"project_id": ["required"]}, code=400)

    db = SessionLocal()
    try:
        service = MemberService(db)
        error = service.remove_member(project_id, member_user_id, current_user.id)
        if error:
            code = 404 if error == Messages.MEMBER_NOT_FOUND else 403
            return APIResponse.error(message=error, code=code)

        return APIResponse.success(message=Messages.MEMBER_REMOVED)
    except Exception as e:
        db.rollback()
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()

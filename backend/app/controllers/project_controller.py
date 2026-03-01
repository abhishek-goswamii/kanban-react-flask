from flask import Blueprint, request
from marshmallow import ValidationError

from app.core.constants import Messages
from app.core.response import APIResponse
from app.core.database import SessionLocal
from app.middleware.auth_middleware import auth_required
from app.services.project_service import ProjectService
from app.schemas.project_schema import CreateProjectSchema, UpdateProjectSchema

project_bp = Blueprint("projects", __name__)


@project_bp.route("", methods=["POST"])
@auth_required
def create_project(current_user):
    """create a new project"""
    schema = CreateProjectSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors=err.messages, code=400)

    db = SessionLocal()
    try:
        service = ProjectService(db)
        project = service.create_project(
            name=data["name"],
            description=data.get("description", ""),
            owner_id=current_user.id,
        )
        return APIResponse.success(data=project.to_dict(), message=Messages.PROJECT_CREATED, code=201)
    except Exception as e:
        db.rollback()
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()


@project_bp.route("", methods=["GET"])
@auth_required
def get_projects(current_user):
    """get all projects for current user"""
    db = SessionLocal()
    try:
        service = ProjectService(db)
        projects = service.get_user_projects(current_user.id)
        return APIResponse.success(data=projects)
    except Exception as e:
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()


@project_bp.route("/<int:project_id>", methods=["GET"])
@auth_required
def get_project(current_user, project_id):
    """get single project with stages"""
    db = SessionLocal()
    try:
        service = ProjectService(db)
        project, error = service.get_project(project_id, current_user.id)
        if error:
            code = 404 if error == Messages.PROJECT_NOT_FOUND else 403
            return APIResponse.error(message=error, code=code)

        return APIResponse.success(data=project)
    except Exception as e:
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()


@project_bp.route("/<int:project_id>", methods=["PUT"])
@auth_required
def update_project(current_user, project_id):
    """update a project"""
    schema = UpdateProjectSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors=err.messages, code=400)

    db = SessionLocal()
    try:
        service = ProjectService(db)
        project, error = service.update_project(
            project_id=project_id,
            user_id=current_user.id,
            name=data.get("name"),
            description=data.get("description"),
        )
        if error:
            code = 404 if error == Messages.PROJECT_NOT_FOUND else 403
            return APIResponse.error(message=error, code=code)

        return APIResponse.success(data=project.to_dict(), message=Messages.PROJECT_UPDATED)
    except Exception as e:
        db.rollback()
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()


@project_bp.route("/<int:project_id>", methods=["DELETE"])
@auth_required
def delete_project(current_user, project_id):
    """delete a project"""
    db = SessionLocal()
    try:
        service = ProjectService(db)
        error = service.delete_project(project_id, current_user.id)
        if error:
            code = 404 if error == Messages.PROJECT_NOT_FOUND else 403
            return APIResponse.error(message=error, code=code)

        return APIResponse.success(message=Messages.PROJECT_DELETED)
    except Exception as e:
        db.rollback()
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()

from flask import Blueprint, request
from marshmallow import ValidationError

from app.core.constants import Messages
from app.core.response import APIResponse
from app.core.database import SessionLocal
from app.middleware.auth_middleware import auth_required
from app.services.task_service import TaskService
from app.schemas.task_schema import CreateTaskSchema, UpdateTaskSchema, MoveTaskSchema

task_bp = Blueprint("tasks", __name__)


@task_bp.route("", methods=["POST"])
@auth_required
def create_task(current_user):
    """create a new task"""
    schema = CreateTaskSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors=err.messages, code=400)

    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors={"project_id": ["required"]}, code=400)

    db = SessionLocal()
    try:
        service = TaskService(db)
        task, error = service.create_task(
            title=data["title"],
            description=data.get("description", ""),
            project_id=project_id,
            stage_id=data["stage_id"],
            created_by=current_user.id,
            assignee_id=data.get("assignee_id"),
        )
        if error:
            code = 404 if error in [Messages.STAGE_NOT_FOUND] else 403
            return APIResponse.error(message=error, code=code)

        return APIResponse.success(data=task.to_dict(), message=Messages.TASK_CREATED, code=201)
    except Exception as e:
        db.rollback()
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()


@task_bp.route("", methods=["GET"])
@auth_required
def get_tasks(current_user):
    """get all tasks for a project"""
    project_id = request.args.get("project_id", type=int)
    if not project_id:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors={"project_id": ["required"]}, code=400)

    db = SessionLocal()
    try:
        service = TaskService(db)
        tasks, error = service.get_tasks_by_project(project_id, current_user.id)
        if error:
            return APIResponse.error(message=error, code=403)

        return APIResponse.success(data=tasks)
    except Exception as e:
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()


@task_bp.route("/<int:task_id>", methods=["GET"])
@auth_required
def get_task(current_user, task_id):
    """get single task detail"""
    db = SessionLocal()
    try:
        service = TaskService(db)
        task, error = service.get_task(task_id, current_user.id)
        if error:
            code = 404 if error == Messages.TASK_NOT_FOUND else 403
            return APIResponse.error(message=error, code=code)

        return APIResponse.success(data=task)
    except Exception as e:
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()


@task_bp.route("/<int:task_id>", methods=["PUT"])
@auth_required
def update_task(current_user, task_id):
    """update a task"""
    schema = UpdateTaskSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors=err.messages, code=400)

    db = SessionLocal()
    try:
        service = TaskService(db)
        task, error = service.update_task(
            task_id=task_id,
            user_id=current_user.id,
            title=data.get("title"),
            description=data.get("description"),
            assignee_id=data.get("assignee_id"),
        )
        if error:
            code = 404 if error == Messages.TASK_NOT_FOUND else 403
            return APIResponse.error(message=error, code=code)

        return APIResponse.success(data=task.to_dict(), message=Messages.TASK_UPDATED)
    except Exception as e:
        db.rollback()
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()


@task_bp.route("/<int:task_id>/move", methods=["PUT"])
@auth_required
def move_task(current_user, task_id):
    """move task to different stage/position (drag & drop)"""
    schema = MoveTaskSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors=err.messages, code=400)

    db = SessionLocal()
    try:
        service = TaskService(db)
        task, error = service.move_task(
            task_id=task_id,
            user_id=current_user.id,
            stage_id=data["stage_id"],
            position=data["position"],
        )
        if error:
            code = 404 if error in [Messages.TASK_NOT_FOUND, Messages.STAGE_NOT_FOUND] else 403
            return APIResponse.error(message=error, code=code)

        return APIResponse.success(data=task.to_dict(), message=Messages.TASK_MOVED)
    except Exception as e:
        db.rollback()
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()


@task_bp.route("/<int:task_id>", methods=["DELETE"])
@auth_required
def delete_task(current_user, task_id):
    """delete a task"""
    db = SessionLocal()
    try:
        service = TaskService(db)
        error = service.delete_task(task_id, current_user.id)
        if error:
            code = 404 if error == Messages.TASK_NOT_FOUND else 403
            return APIResponse.error(message=error, code=code)

        return APIResponse.success(message=Messages.TASK_DELETED)
    except Exception as e:
        db.rollback()
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()

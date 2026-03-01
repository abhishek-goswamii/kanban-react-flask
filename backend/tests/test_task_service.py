import pytest
from unittest.mock import MagicMock, patch
from app.services.task_service import TaskService
from app.models.task import Task
from app.models.stage import Stage
from app.models.project_member import ProjectMember
from app.core.constants import Messages


class TestTaskServiceCreate:
    """tests for task creation"""

    def test_create_task_success(self, mock_db):
        """should create task when user is member and stage is valid"""
        with patch.object(TaskService, "__init__", lambda self, db: None):
            service = TaskService(mock_db)
            service.db = mock_db
            service.task_repo = MagicMock()
            service.stage_repo = MagicMock()
            service.member_repo = MagicMock()

            mock_membership = MagicMock(spec=ProjectMember)
            mock_membership.status = "accepted"
            service.member_repo.find_by_project_and_user.return_value = mock_membership

            mock_stage = MagicMock(spec=Stage)
            mock_stage.project_id = 1
            service.stage_repo.find_by_id.return_value = mock_stage
            service.task_repo.get_max_position.return_value = 2

            mock_task = MagicMock(spec=Task)
            mock_task.id = 1
            service.task_repo.create.return_value = mock_task

            task, error = service.create_task("Test Task", "desc", project_id=1, stage_id=1, created_by=1)

            assert task is not None
            assert error is None

    def test_create_task_not_member(self, mock_db):
        """should return error when user is not member"""
        with patch.object(TaskService, "__init__", lambda self, db: None):
            service = TaskService(mock_db)
            service.member_repo = MagicMock()
            service.stage_repo = MagicMock()
            service.task_repo = MagicMock()
            service.member_repo.find_by_project_and_user.return_value = None

            task, error = service.create_task("Test", "desc", project_id=1, stage_id=1, created_by=99)

            assert task is None
            assert error == Messages.FORBIDDEN

    def test_create_task_invalid_stage(self, mock_db):
        """should return error when stage doesn't belong to project"""
        with patch.object(TaskService, "__init__", lambda self, db: None):
            service = TaskService(mock_db)
            service.member_repo = MagicMock()
            service.stage_repo = MagicMock()
            service.task_repo = MagicMock()

            mock_membership = MagicMock(spec=ProjectMember)
            mock_membership.status = "accepted"
            service.member_repo.find_by_project_and_user.return_value = mock_membership
            service.stage_repo.find_by_id.return_value = None

            task, error = service.create_task("Test", "desc", project_id=1, stage_id=999, created_by=1)

            assert task is None
            assert error == Messages.STAGE_NOT_FOUND


class TestTaskServiceMove:
    """tests for moving tasks between stages"""

    def test_move_task_success(self, mock_db):
        """should move task to new stage and position"""
        with patch.object(TaskService, "__init__", lambda self, db: None):
            service = TaskService(mock_db)
            service.task_repo = MagicMock()
            service.stage_repo = MagicMock()
            service.member_repo = MagicMock()

            mock_task = MagicMock(spec=Task)
            mock_task.project_id = 1
            service.task_repo.find_by_id.return_value = mock_task

            mock_membership = MagicMock(spec=ProjectMember)
            mock_membership.status = "accepted"
            service.member_repo.find_by_project_and_user.return_value = mock_membership

            mock_stage = MagicMock(spec=Stage)
            mock_stage.project_id = 1
            service.stage_repo.find_by_id.return_value = mock_stage

            service.task_repo.update.return_value = mock_task

            task, error = service.move_task(task_id=1, user_id=1, stage_id=2, position=0)

            assert task is not None
            assert error is None
            assert mock_task.stage_id == 2
            assert mock_task.position == 0

    def test_move_task_not_found(self, mock_db):
        """should return error when task doesn't exist"""
        with patch.object(TaskService, "__init__", lambda self, db: None):
            service = TaskService(mock_db)
            service.task_repo = MagicMock()
            service.task_repo.find_by_id.return_value = None

            task, error = service.move_task(task_id=999, user_id=1, stage_id=2, position=0)

            assert task is None
            assert error == Messages.TASK_NOT_FOUND


class TestTaskServiceDelete:
    """tests for task deletion"""

    def test_delete_task_success(self, mock_db):
        """should delete task when user is a member"""
        with patch.object(TaskService, "__init__", lambda self, db: None):
            service = TaskService(mock_db)
            service.task_repo = MagicMock()
            service.member_repo = MagicMock()

            mock_task = MagicMock(spec=Task)
            mock_task.project_id = 1
            service.task_repo.find_by_id.return_value = mock_task

            mock_membership = MagicMock(spec=ProjectMember)
            mock_membership.status = "accepted"
            service.member_repo.find_by_project_and_user.return_value = mock_membership

            error = service.delete_task(task_id=1, user_id=1)

            assert error is None
            service.task_repo.delete.assert_called_once()

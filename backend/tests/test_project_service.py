import pytest
from unittest.mock import MagicMock, patch
from app.services.project_service import ProjectService
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.core.constants import Messages, ProjectRole


class TestProjectServiceCreate:
    """tests for project creation"""

    def test_create_project_success(self, mock_db):
        """should create project with default stages and owner membership"""
        with patch.object(ProjectService, "__init__", lambda self, db: None):
            service = ProjectService(mock_db)
            service.db = mock_db
            service.project_repo = MagicMock()
            service.stage_repo = MagicMock()
            service.member_repo = MagicMock()

            mock_project = MagicMock(spec=Project)
            mock_project.id = 1
            service.project_repo.create.return_value = mock_project

            result = service.create_project("Test Project", "desc", owner_id=1)

            assert result.id == 1
            service.project_repo.create.assert_called_once()
            # 4 default stages created
            assert service.stage_repo.create.call_count == 4
            # owner added as member
            service.member_repo.create.assert_called_once()


class TestProjectServiceGet:
    """tests for fetching projects"""

    def test_get_project_not_found(self, mock_db):
        """should return error when project doesn't exist"""
        with patch.object(ProjectService, "__init__", lambda self, db: None):
            service = ProjectService(mock_db)
            service.project_repo = MagicMock()
            service.member_repo = MagicMock()
            service.stage_repo = MagicMock()
            service.project_repo.find_by_id.return_value = None

            result, error = service.get_project(999, user_id=1)

            assert result is None
            assert error == Messages.PROJECT_NOT_FOUND

    def test_get_project_forbidden(self, mock_db):
        """should return error when user is not a member"""
        with patch.object(ProjectService, "__init__", lambda self, db: None):
            service = ProjectService(mock_db)
            service.project_repo = MagicMock()
            service.member_repo = MagicMock()
            service.stage_repo = MagicMock()
            service.project_repo.find_by_id.return_value = MagicMock(spec=Project)
            service.member_repo.find_by_project_and_user.return_value = None

            result, error = service.get_project(1, user_id=99)

            assert result is None
            assert error == Messages.FORBIDDEN


class TestProjectServiceDelete:
    """tests for project deletion"""

    def test_delete_project_not_owner(self, mock_db):
        """should return error when non-owner tries to delete"""
        with patch.object(ProjectService, "__init__", lambda self, db: None):
            service = ProjectService(mock_db)
            service.project_repo = MagicMock()
            mock_project = MagicMock(spec=Project)
            mock_project.owner_id = 1
            service.project_repo.find_by_id.return_value = mock_project

            error = service.delete_project(1, user_id=2)

            assert error == Messages.FORBIDDEN
            service.project_repo.delete.assert_not_called()

    def test_delete_project_success(self, mock_db):
        """should delete project when user is owner"""
        with patch.object(ProjectService, "__init__", lambda self, db: None):
            service = ProjectService(mock_db)
            service.project_repo = MagicMock()
            mock_project = MagicMock(spec=Project)
            mock_project.owner_id = 1
            service.project_repo.find_by_id.return_value = mock_project

            error = service.delete_project(1, user_id=1)

            assert error is None
            service.project_repo.delete.assert_called_once()

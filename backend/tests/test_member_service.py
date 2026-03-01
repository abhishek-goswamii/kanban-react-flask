import pytest
from unittest.mock import MagicMock, patch
from app.services.member_service import MemberService
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.core.constants import Messages, ProjectRole, InvitationStatus


class TestMemberServiceInvite:
    """tests for member invitation"""

    def test_invite_success(self, mock_db):
        """should invite a user to a project"""
        with patch.object(MemberService, "__init__", lambda self, db: None):
            service = MemberService(mock_db)
            service.member_repo = MagicMock()
            service.project_repo = MagicMock()
            service.user_repo = MagicMock()

            # inviter is owner
            mock_inviter = MagicMock(spec=ProjectMember)
            mock_inviter.role = ProjectRole.OWNER
            service.member_repo.find_by_project_and_user.side_effect = [mock_inviter, None]

            # user exists
            mock_user = MagicMock(spec=User)
            mock_user.id = 2
            service.user_repo.find_by_email.return_value = mock_user

            mock_member = MagicMock(spec=ProjectMember)
            service.member_repo.create.return_value = mock_member

            member, error = service.invite_member(project_id=1, email="new@test.com", role=ProjectRole.MEMBER, inviter_id=1)

            assert member is not None
            assert error is None

    def test_invite_forbidden(self, mock_db):
        """should reject invitation from non-admin/non-owner"""
        with patch.object(MemberService, "__init__", lambda self, db: None):
            service = MemberService(mock_db)
            service.member_repo = MagicMock()
            service.user_repo = MagicMock()

            mock_inviter = MagicMock(spec=ProjectMember)
            mock_inviter.role = ProjectRole.MEMBER
            service.member_repo.find_by_project_and_user.return_value = mock_inviter

            member, error = service.invite_member(project_id=1, email="x@test.com", role=ProjectRole.MEMBER, inviter_id=3)

            assert member is None
            assert error == Messages.FORBIDDEN

    def test_invite_user_not_found(self, mock_db):
        """should return error when invited user doesn't exist"""
        with patch.object(MemberService, "__init__", lambda self, db: None):
            service = MemberService(mock_db)
            service.member_repo = MagicMock()
            service.user_repo = MagicMock()

            mock_inviter = MagicMock(spec=ProjectMember)
            mock_inviter.role = ProjectRole.OWNER
            service.member_repo.find_by_project_and_user.return_value = mock_inviter
            service.user_repo.find_by_email.return_value = None

            member, error = service.invite_member(project_id=1, email="nope@test.com", role=ProjectRole.MEMBER, inviter_id=1)

            assert member is None
            assert error == Messages.USER_NOT_FOUND

    def test_invite_already_member(self, mock_db):
        """should return error when user is already a member"""
        with patch.object(MemberService, "__init__", lambda self, db: None):
            service = MemberService(mock_db)
            service.member_repo = MagicMock()
            service.user_repo = MagicMock()

            mock_inviter = MagicMock(spec=ProjectMember)
            mock_inviter.role = ProjectRole.OWNER
            service.member_repo.find_by_project_and_user.side_effect = [
                mock_inviter,
                MagicMock(spec=ProjectMember),  # already member
            ]

            mock_user = MagicMock(spec=User)
            mock_user.id = 2
            service.user_repo.find_by_email.return_value = mock_user

            member, error = service.invite_member(project_id=1, email="dup@test.com", role=ProjectRole.MEMBER, inviter_id=1)

            assert member is None
            assert error == Messages.ALREADY_A_MEMBER


class TestMemberServiceRemove:
    """tests for member removal"""

    def test_remove_owner_fails(self, mock_db):
        """should not allow removing the project owner"""
        with patch.object(MemberService, "__init__", lambda self, db: None):
            service = MemberService(mock_db)
            service.member_repo = MagicMock()

            mock_remover = MagicMock(spec=ProjectMember)
            mock_remover.role = ProjectRole.OWNER

            mock_target = MagicMock(spec=ProjectMember)
            mock_target.role = ProjectRole.OWNER

            service.member_repo.find_by_project_and_user.side_effect = [mock_remover, mock_target]

            error = service.remove_member(project_id=1, member_user_id=1, remover_id=1)

            assert error == Messages.CANNOT_REMOVE_OWNER
            service.member_repo.delete.assert_not_called()

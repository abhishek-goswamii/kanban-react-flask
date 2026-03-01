from typing import Tuple, Optional, List

from sqlalchemy.orm import Session
from app.core.constants import Messages, ProjectRole, InvitationStatus
from app.models.project_member import ProjectMember
from app.repositories.member_repository import MemberRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository


class MemberService:
    """handles member invitation and management business logic"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.member_repo = MemberRepository(db)
        self.project_repo = ProjectRepository(db)
        self.user_repo = UserRepository(db)

    def add_member(
        self, project_id: int, email: str, role: str, adder_id: int
    ) -> Tuple[Optional[ProjectMember], Optional[str]]:
        """directly adds a user to a project"""
        # verify adder is owner or admin
        adder_membership = self.member_repo.find_by_project_and_user(project_id, adder_id)
        if not adder_membership or adder_membership.role not in [ProjectRole.OWNER, ProjectRole.ADMIN]:
            return None, Messages.FORBIDDEN

        # find user by email
        user = self.user_repo.find_by_email(email)
        if not user:
            return None, Messages.USER_NOT_FOUND

        # check if already a member
        existing = self.member_repo.find_by_project_and_user(project_id, user.id)
        if existing:
            return None, Messages.ALREADY_A_MEMBER

        member = ProjectMember(
            project_id=project_id,
            user_id=user.id,
            role=role,
            status=InvitationStatus.ACCEPTED,
        )
        created = self.member_repo.create(member)
        return created, None


    def get_members(self, project_id: int, user_id: int) -> Tuple[Optional[List[dict]], Optional[str]]:
        """returns all members of a project"""
        membership = self.member_repo.find_by_project_and_user(project_id, user_id)
        if not membership or membership.status != "accepted":
            return None, Messages.FORBIDDEN

        members = self.member_repo.find_by_project(project_id)
        return [m.to_dict() for m in members], None

    def get_pending_invitations(self, user_id: int) -> List[dict]:
        """returns all pending invitations for user"""
        invitations = self.member_repo.find_pending_invitations(user_id)
        result = []
        for inv in invitations:
            project = self.project_repo.find_by_id(inv.project_id)
            inv_dict = inv.to_dict()
            inv_dict["project_name"] = project.name if project else None
            result.append(inv_dict)
        return result

    def remove_member(self, project_id: int, member_user_id: int, remover_id: int) -> Optional[str]:
        """removes a member from a project"""
        # check remover is owner or admin
        remover_membership = self.member_repo.find_by_project_and_user(project_id, remover_id)
        if not remover_membership or remover_membership.role not in [ProjectRole.OWNER, ProjectRole.ADMIN]:
            return Messages.FORBIDDEN

        # find target member
        target = self.member_repo.find_by_project_and_user(project_id, member_user_id)
        if not target:
            return Messages.MEMBER_NOT_FOUND

        # cannot remove owner
        if target.role == ProjectRole.OWNER:
            return Messages.CANNOT_REMOVE_OWNER

        self.member_repo.delete(target)
        return None

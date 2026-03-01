from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.project_member import ProjectMember


class MemberRepository:
    """handles all project member db operations"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_id(self, member_id: int) -> Optional[ProjectMember]:
        return self.db.query(ProjectMember).filter(ProjectMember.id == member_id).first()

    def find_by_project_and_user(self, project_id: int, user_id: int) -> Optional[ProjectMember]:
        return (
            self.db.query(ProjectMember)
            .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
            .first()
        )

    def find_by_project(self, project_id: int) -> List[ProjectMember]:
        return self.db.query(ProjectMember).filter(ProjectMember.project_id == project_id).all()

    def find_user_projects(self, user_id: int) -> List[ProjectMember]:
        return self.db.query(ProjectMember).filter(ProjectMember.user_id == user_id).all()

    def find_pending_invitations(self, user_id: int) -> List[ProjectMember]:
        return (
            self.db.query(ProjectMember)
            .filter(ProjectMember.user_id == user_id, ProjectMember.status == "pending")
            .all()
        )

    def create(self, member: ProjectMember) -> ProjectMember:
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def update(self, member: ProjectMember) -> ProjectMember:
        self.db.commit()
        self.db.refresh(member)
        return member

    def delete(self, member: ProjectMember) -> None:
        self.db.delete(member)
        self.db.commit()

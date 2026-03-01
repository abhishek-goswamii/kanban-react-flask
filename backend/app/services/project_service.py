from typing import Tuple, Optional, List

from sqlalchemy.orm import Session
from app.core.constants import Messages, ProjectRole, TaskStatus
from app.models.project import Project
from app.models.stage import Stage
from app.models.project_member import ProjectMember
from app.repositories.project_repository import ProjectRepository
from app.repositories.stage_repository import StageRepository
from app.repositories.member_repository import MemberRepository

# default stages for a new project
DEFAULT_STAGES = [
    {"name": "To Do", "position": 0},
    {"name": "In Progress", "position": 1},
    {"name": "In Review", "position": 2},
    {"name": "Done", "position": 3},
]


class ProjectService:
    """handles project business logic"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.stage_repo = StageRepository(db)
        self.member_repo = MemberRepository(db)

    def create_project(self, name: str, description: str, owner_id: int) -> Project:
        """creates project with default stages and adds owner as member"""
        project = Project(name=name, description=description, owner_id=owner_id)
        created = self.project_repo.create(project)

        # create default stages
        for stage_data in DEFAULT_STAGES:
            stage = Stage(
                name=stage_data["name"],
                position=stage_data["position"],
                project_id=created.id,
            )
            self.stage_repo.create(stage)

        # add owner as member
        member = ProjectMember(
            project_id=created.id,
            user_id=owner_id,
            role=ProjectRole.OWNER,
            status="accepted",
        )
        self.member_repo.create(member)

        return created

    def get_user_projects(self, user_id: int) -> List[dict]:
        """returns all projects the user is a member of"""
        memberships = self.member_repo.find_user_projects(user_id)
        result = []
        for membership in memberships:
            if membership.status == "accepted":
                project = self.project_repo.find_by_id(membership.project_id)
                if project:
                    project_dict = project.to_dict()
                    project_dict["role"] = membership.role
                    result.append(project_dict)
        return result

    def get_project(self, project_id: int, user_id: int) -> Tuple[Optional[dict], Optional[str]]:
        """returns project with stages if user is a member"""
        project = self.project_repo.find_by_id(project_id)
        if not project:
            return None, Messages.PROJECT_NOT_FOUND

        membership = self.member_repo.find_by_project_and_user(project_id, user_id)
        if not membership or membership.status != "accepted":
            return None, Messages.FORBIDDEN

        stages = self.stage_repo.find_by_project(project_id)
        project_dict = project.to_dict()
        project_dict["stages"] = [s.to_dict() for s in stages]
        project_dict["role"] = membership.role
        return project_dict, None

    def update_project(
        self, project_id: int, user_id: int, name: Optional[str] = None, description: Optional[str] = None
    ) -> Tuple[Optional[Project], Optional[str]]:
        """updates project if user is owner or admin"""
        project = self.project_repo.find_by_id(project_id)
        if not project:
            return None, Messages.PROJECT_NOT_FOUND

        membership = self.member_repo.find_by_project_and_user(project_id, user_id)
        if not membership or membership.role not in [ProjectRole.OWNER, ProjectRole.ADMIN]:
            return None, Messages.FORBIDDEN

        if name is not None:
            project.name = name
        if description is not None:
            project.description = description

        updated = self.project_repo.update(project)
        return updated, None

    def delete_project(self, project_id: int, user_id: int) -> Optional[str]:
        """deletes project if user is owner"""
        project = self.project_repo.find_by_id(project_id)
        if not project:
            return Messages.PROJECT_NOT_FOUND

        if project.owner_id != user_id:
            return Messages.FORBIDDEN

        self.project_repo.delete(project)
        return None

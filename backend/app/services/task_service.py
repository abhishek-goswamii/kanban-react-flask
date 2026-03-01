from typing import Tuple, Optional, List

from sqlalchemy.orm import Session
from app.core.constants import Messages
from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.repositories.stage_repository import StageRepository
from app.repositories.member_repository import MemberRepository


class TaskService:
    """handles task business logic"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.task_repo = TaskRepository(db)
        self.stage_repo = StageRepository(db)
        self.member_repo = MemberRepository(db)

    def create_task(
        self,
        title: str,
        description: str,
        project_id: int,
        stage_id: int,
        created_by: int,
        assignee_id: Optional[int] = None,
    ) -> Tuple[Optional[Task], Optional[str]]:
        """creates a new task at end of stage"""
        # verify membership
        membership = self.member_repo.find_by_project_and_user(project_id, created_by)
        if not membership or membership.status != "accepted":
            return None, Messages.FORBIDDEN

        # verify stage belongs to project
        stage = self.stage_repo.find_by_id(stage_id)
        if not stage or stage.project_id != project_id:
            return None, Messages.STAGE_NOT_FOUND

        position = self.task_repo.get_max_position(stage_id) + 1

        task = Task(
            title=title,
            description=description,
            position=position,
            project_id=project_id,
            stage_id=stage_id,
            assignee_id=assignee_id,
            created_by=created_by,
        )
        created = self.task_repo.create(task)
        return created, None

    def get_tasks_by_project(self, project_id: int, user_id: int) -> Tuple[Optional[List[dict]], Optional[str]]:
        """returns all tasks for a project, grouped by stage"""
        membership = self.member_repo.find_by_project_and_user(project_id, user_id)
        if not membership or membership.status != "accepted":
            return None, Messages.FORBIDDEN

        tasks = self.task_repo.find_by_project(project_id)
        return [t.to_dict() for t in tasks], None

    def get_task(self, task_id: int, user_id: int) -> Tuple[Optional[dict], Optional[str]]:
        """returns single task detail"""
        task = self.task_repo.find_by_id(task_id)
        if not task:
            return None, Messages.TASK_NOT_FOUND

        membership = self.member_repo.find_by_project_and_user(task.project_id, user_id)
        if not membership or membership.status != "accepted":
            return None, Messages.FORBIDDEN

        return task.to_dict(), None

    def update_task(
        self,
        task_id: int,
        user_id: int,
        **kwargs
    ) -> Tuple[Optional[Task], Optional[str]]:
        """updates task details"""
        task = self.task_repo.find_by_id(task_id)
        if not task:
            return None, Messages.TASK_NOT_FOUND

        membership = self.member_repo.find_by_project_and_user(task.project_id, user_id)
        if not membership or membership.status != "accepted":
            return None, Messages.FORBIDDEN

        if "title" in kwargs and kwargs["title"] is not None:
            task.title = kwargs["title"]
        if "description" in kwargs and kwargs["description"] is not None:
            task.description = kwargs["description"]
        if "assignee_id" in kwargs:
            task.assignee_id = kwargs["assignee_id"]

        updated = self.task_repo.update(task)
        return updated, None


    def move_task(self, task_id: int, user_id: int, stage_id: int, position: int) -> Tuple[Optional[Task], Optional[str]]:
        """moves task to a different stage and/or position"""
        task = self.task_repo.find_by_id(task_id)
        if not task:
            return None, Messages.TASK_NOT_FOUND

        membership = self.member_repo.find_by_project_and_user(task.project_id, user_id)
        if not membership or membership.status != "accepted":
            return None, Messages.FORBIDDEN

        # verify target stage
        stage = self.stage_repo.find_by_id(stage_id)
        if not stage or stage.project_id != task.project_id:
            return None, Messages.STAGE_NOT_FOUND

        task.stage_id = stage_id
        task.position = position

        updated = self.task_repo.update(task)
        return updated, None

    def delete_task(self, task_id: int, user_id: int) -> Optional[str]:
        """deletes a task"""
        task = self.task_repo.find_by_id(task_id)
        if not task:
            return Messages.TASK_NOT_FOUND

        membership = self.member_repo.find_by_project_and_user(task.project_id, user_id)
        if not membership or membership.status != "accepted":
            return Messages.FORBIDDEN

        self.task_repo.delete(task)
        return None

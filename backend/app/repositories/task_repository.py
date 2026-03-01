from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.task import Task


class TaskRepository:
    """handles all task db operations"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_id(self, task_id: int) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def find_by_project(self, project_id: int) -> List[Task]:
        return self.db.query(Task).filter(Task.project_id == project_id).all()

    def find_by_stage(self, stage_id: int) -> List[Task]:
        return (
            self.db.query(Task)
            .filter(Task.stage_id == stage_id)
            .order_by(Task.position)
            .all()
        )

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task: Task) -> Task:
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.commit()

    def get_max_position(self, stage_id: int) -> int:
        """returns the current max position in a stage"""
        from sqlalchemy import func
        result = self.db.query(func.max(Task.position)).filter(Task.stage_id == stage_id).scalar()
        return result if result is not None else -1

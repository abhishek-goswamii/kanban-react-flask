from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.project import Project


class ProjectRepository:
    """handles all project db operations"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_id(self, project_id: int) -> Optional[Project]:
        return self.db.query(Project).filter(Project.id == project_id).first()

    def find_by_owner(self, owner_id: int) -> List[Project]:
        return self.db.query(Project).filter(Project.owner_id == owner_id).all()

    def create(self, project: Project) -> Project:
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project: Project) -> Project:
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        self.db.delete(project)
        self.db.commit()

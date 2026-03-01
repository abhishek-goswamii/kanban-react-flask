from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.stage import Stage


class StageRepository:
    """handles all stage db operations"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_id(self, stage_id: int) -> Optional[Stage]:
        return self.db.query(Stage).filter(Stage.id == stage_id).first()

    def find_by_project(self, project_id: int) -> List[Stage]:
        return (
            self.db.query(Stage)
            .filter(Stage.project_id == project_id)
            .order_by(Stage.position)
            .all()
        )

    def create(self, stage: Stage) -> Stage:
        self.db.add(stage)
        self.db.commit()
        self.db.refresh(stage)
        return stage

    def delete(self, stage: Stage) -> None:
        self.db.delete(stage)
        self.db.commit()

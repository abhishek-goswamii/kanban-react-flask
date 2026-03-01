from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.comment import Comment


class CommentRepository:
    """handles all comment db operations"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_id(self, comment_id: int) -> Optional[Comment]:
        return self.db.query(Comment).filter(Comment.id == comment_id).first()

    def find_by_task(self, task_id: int) -> List[Comment]:
        return (
            self.db.query(Comment)
            .filter(Comment.task_id == task_id)
            .order_by(Comment.created_at.desc())
            .all()
        )

    def create(self, comment: Comment) -> Comment:
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete(self, comment: Comment) -> None:
        self.db.delete(comment)
        self.db.commit()

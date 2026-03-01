from typing import Tuple, Optional, List

from sqlalchemy.orm import Session
from app.core.constants import Messages
from app.models.comment import Comment
from app.repositories.comment_repository import CommentRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.member_repository import MemberRepository


class CommentService:
    """handles comment business logic"""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.comment_repo = CommentRepository(db)
        self.task_repo = TaskRepository(db)
        self.member_repo = MemberRepository(db)

    def add_comment(
        self, task_id: int, content: str, author_id: int
    ) -> Tuple[Optional[Comment], Optional[str]]:
        """adds a comment to a task"""
        task = self.task_repo.find_by_id(task_id)
        if not task:
            return None, Messages.TASK_NOT_FOUND

        membership = self.member_repo.find_by_project_and_user(task.project_id, author_id)
        if not membership or membership.status != "accepted":
            return None, Messages.FORBIDDEN

        comment = Comment(
            content=content,
            task_id=task_id,
            author_id=author_id,
        )
        created = self.comment_repo.create(comment)
        return created, None

    def get_comments(self, task_id: int, user_id: int) -> Tuple[Optional[List[dict]], Optional[str]]:
        """returns all comments for a task"""
        task = self.task_repo.find_by_id(task_id)
        if not task:
            return None, Messages.TASK_NOT_FOUND

        membership = self.member_repo.find_by_project_and_user(task.project_id, user_id)
        if not membership or membership.status != "accepted":
            return None, Messages.FORBIDDEN

        comments = self.comment_repo.find_by_task(task_id)
        return [c.to_dict() for c in comments], None

    def delete_comment(self, comment_id: int, user_id: int) -> Optional[str]:
        """deletes a comment (only author can delete)"""
        comment = self.comment_repo.find_by_id(comment_id)
        if not comment:
            return Messages.COMMENT_NOT_FOUND

        if comment.author_id != user_id:
            return Messages.FORBIDDEN

        self.comment_repo.delete(comment)
        return None

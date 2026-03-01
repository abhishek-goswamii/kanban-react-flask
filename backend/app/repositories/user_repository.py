from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    """handles all user db operations"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def find_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

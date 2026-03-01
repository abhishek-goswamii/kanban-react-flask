from typing import Tuple, Optional
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from app.core.config import JWT_SECRET_KEY, JWT_TOKEN_EXPIRY_HOURS, JWT_COOKIE_NAME
from app.core.constants import Messages
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """handles authentication business logic"""

    def __init__(self, db: Session) -> None:
        self.user_repo = UserRepository(db)

    def register(self, email: str, full_name: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """registers a new user, returns (user, error)"""
        existing = self.user_repo.find_by_email(email)
        if existing:
            return None, Messages.EMAIL_ALREADY_EXISTS

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user = User(
            email=email,
            full_name=full_name,
            password_hash=password_hash,
        )
        created_user = self.user_repo.create(user)
        return created_user, None

    def login(self, email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
        """authenticates user, returns (token, error)"""
        user = self.user_repo.find_by_email(email)
        if not user:
            return None, Messages.INVALID_CREDENTIALS

        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            return None, Messages.INVALID_CREDENTIALS

        token = self._generate_token(user.id)
        return token, None

    def get_current_user(self, token: str) -> Tuple[Optional[User], Optional[str]]:
        """decodes token and returns user"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if not user_id:
                return None, Messages.TOKEN_INVALID
            user = self.user_repo.find_by_id(user_id)
            if not user:
                return None, Messages.TOKEN_INVALID
            return user, None
        except jwt.ExpiredSignatureError:
            return None, Messages.TOKEN_EXPIRED
        except jwt.InvalidTokenError:
            return None, Messages.TOKEN_INVALID

    @staticmethod
    def _generate_token(user_id: int) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_TOKEN_EXPIRY_HOURS),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

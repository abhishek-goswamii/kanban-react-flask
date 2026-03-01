from functools import wraps
from flask import request

from app.core.config import JWT_COOKIE_NAME
from app.core.constants import Messages
from app.core.response import APIResponse
from app.core.database import SessionLocal
from app.services.auth_service import AuthService


def auth_required(f):
    """decorator that verifies jwt cookie and injects current_user"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get(JWT_COOKIE_NAME)
        if not token:
            return APIResponse.error(message=Messages.UNAUTHORIZED, code=401)

        db = SessionLocal()
        try:
            service = AuthService(db)
            user, error = service.get_current_user(token)
            if error:
                return APIResponse.error(message=error, code=401)

            return f(current_user=user, *args, **kwargs)
        except Exception as e:
            return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
        finally:
            db.close()

    return decorated

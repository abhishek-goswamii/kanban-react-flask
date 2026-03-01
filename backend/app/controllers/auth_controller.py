from flask import Blueprint, request, make_response
from marshmallow import ValidationError

from app.core.config import JWT_COOKIE_NAME
from app.core.constants import Messages
from app.core.response import APIResponse
from app.core.database import SessionLocal
from app.services.auth_service import AuthService
from app.schemas.auth_schema import RegisterSchema, LoginSchema

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """register a new user"""
    schema = RegisterSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors=err.messages, code=400)

    db = SessionLocal()
    try:
        service = AuthService(db)
        user, error = service.register(
            email=data["email"],
            full_name=data["full_name"],
            password=data["password"],
        )
        if error:
            return APIResponse.error(message=error, code=409)

        return APIResponse.success(data=user.to_dict(), message=Messages.REGISTER_SUCCESS, code=201)
    except Exception as e:
        db.rollback()
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    """login and set jwt cookie"""
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return APIResponse.error(message=Messages.VALIDATION_ERROR, errors=err.messages, code=400)

    db = SessionLocal()
    try:
        service = AuthService(db)
        token, error = service.login(email=data["email"], password=data["password"])
        if error:
            return APIResponse.error(message=error, code=401)

        response = make_response(APIResponse.success(message=Messages.LOGIN_SUCCESS))
        response.set_cookie(
            JWT_COOKIE_NAME,
            token,
            httponly=True,
            secure=False,  # set True in production
            samesite="Lax",
            max_age=86400,
            path="/",
        )
        return response
    except Exception as e:
        db.rollback()
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """logout and clear jwt cookie"""
    response = make_response(APIResponse.success(message=Messages.LOGOUT_SUCCESS))
    response.delete_cookie(JWT_COOKIE_NAME, path="/")
    return response


@auth_bp.route("/me", methods=["GET"])
def me():
    """get current authenticated user"""
    token = request.cookies.get(JWT_COOKIE_NAME)
    if not token:
        return APIResponse.error(message=Messages.UNAUTHORIZED, code=401)

    db = SessionLocal()
    try:
        service = AuthService(db)
        user, error = service.get_current_user(token)
        if error:
            return APIResponse.error(message=error, code=401)

        return APIResponse.success(data=user.to_dict())
    except Exception as e:
        return APIResponse.error(message=Messages.SERVER_ERROR, code=500)
    finally:
        db.close()

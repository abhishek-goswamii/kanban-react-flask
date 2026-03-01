from flask import Flask
from flask_cors import CORS

from app.core.config import configs
from app.core.constants import AppConstants, RouteConstants
from app.core.logger import configure_logger
from app.middleware.logging_middleware import LoggingMiddleware
from app.controllers.auth_controller import auth_bp
from app.controllers.project_controller import project_bp
from app.controllers.task_controller import task_bp
from app.controllers.comment_controller import comment_bp
from app.controllers.member_controller import member_bp


def create_app(env: str = "development") -> Flask:
    """flask application factory"""
    app = Flask(__name__)
    app.config.from_object(configs.get(env, configs["default"]))

    # cors for frontend on port 3202
    CORS(app, supports_credentials=True, origins=["http://localhost:3202"])

    LoggingMiddleware(app)
    configure_logger(app.config["LOG_LEVEL"])

    # register blueprints
    prefix = AppConstants.API_V1_PREFIX
    app.register_blueprint(auth_bp, url_prefix=f"{prefix}{RouteConstants.AUTH}")
    app.register_blueprint(project_bp, url_prefix=f"{prefix}{RouteConstants.PROJECTS}")
    app.register_blueprint(task_bp, url_prefix=f"{prefix}{RouteConstants.TASKS}")
    app.register_blueprint(comment_bp, url_prefix=f"{prefix}{RouteConstants.COMMENTS}")
    app.register_blueprint(member_bp, url_prefix=f"{prefix}{RouteConstants.MEMBERS}")

    return app

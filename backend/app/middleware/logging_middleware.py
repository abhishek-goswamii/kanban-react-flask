from app.core.constants import AppConstants
import uuid
from flask import g, request

class LoggingMiddleware:
    """attaches unique id for tracing requests"""
    def __init__(self, app):
        self.app = app
        @app.before_request
        def before_request():
            """set request context"""
            g.request_id = request.headers.get(AppConstants.REQUEST_ID_HEADER, str(uuid.uuid4()))

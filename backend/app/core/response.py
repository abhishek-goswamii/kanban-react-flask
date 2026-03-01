from flask import jsonify, g
from app.core.constants import AppConstants


class APIResponse:
    """standard api response builder"""

    @staticmethod
    def success(data=None, message=None, code=200):
        """success response format"""
        res = {
            "status": AppConstants.SUCCESS,
            "request_id": g.get("request_id", "system"),
            "data": data,
            "message": message,
        }
        return jsonify(res), code

    @staticmethod
    def error(message=None, code=400, errors=None):
        """error response format"""
        res = {
            "status": AppConstants.ERROR,
            "request_id": g.get("request_id", "system"),
            "message": message,
            "errors": errors,
        }
        return jsonify(res), code

import logging
from flask import g


def configure_logger(lvl: str = "INFO") -> None:
    """configure app logger only, not root"""
    logger = logging.getLogger("app_logger")
    logger.setLevel(getattr(logging, lvl, logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | [%(request_id)s] | %(message)s")
        )
        logger.addHandler(handler)

    # don't propagate to root so we don't break flask/werkzeug logs
    logger.propagate = False


class RequestLogger:
    """custom logger with request context"""

    def __init__(self) -> None:
        self._logger = logging.getLogger("app_logger")

    def _get_request_id(self) -> str:
        """gets id from context"""
        if hasattr(g, "request_id"):
            return g.request_id
        return "system"

    def info(self, msg: str) -> None:
        self._logger.info(msg, extra={"request_id": self._get_request_id()})

    def error(self, msg: str) -> None:
        self._logger.error(msg, extra={"request_id": self._get_request_id()})

    def warning(self, msg: str) -> None:
        self._logger.warning(msg, extra={"request_id": self._get_request_id()})


logger = RequestLogger()

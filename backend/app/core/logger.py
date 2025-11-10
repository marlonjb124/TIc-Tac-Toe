import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from app.core.config import settings


class AppLogger:
    _instance: Optional["AppLogger"] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self) -> None:
        log_dir = Path("/app/logs")
        log_dir.mkdir(exist_ok=True, parents=True)

        self._logger = logging.getLogger("tictactoe")
        self._logger.setLevel(
            logging.DEBUG if settings.DEBUG else logging.INFO
        )
        self._logger.propagate = False

        if self._logger.handlers:
            return

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        file_handler = RotatingFileHandler(
            filename=log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(
            logging.DEBUG if settings.DEBUG else logging.INFO
        )
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

        error_handler = RotatingFileHandler(
            filename=log_dir / "errors.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self._logger.addHandler(error_handler)

    def get_logger(self) -> logging.Logger:
        if self._logger is None:
            self._setup_logger()
        return self._logger


app_logger = AppLogger()
logger = app_logger.get_logger()


def get_logger(name: str = "tictactoe") -> logging.Logger:
    if name == "tictactoe":
        return app_logger.get_logger()
    child_logger = app_logger.get_logger().getChild(name)
    return child_logger

"""
Centralized logging configuration for the application.
Logs to both console and rotating file.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

from app.core.config import settings


class AppLogger:
    """Application logger with file and console handlers."""

    _instance: Optional["AppLogger"] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls):
        """Singleton pattern to ensure one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize logger if not already initialized."""
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self) -> None:
        """Configure logger with file and console handlers."""
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Create logger
        self._logger = logging.getLogger("tictactoe")
        self._logger.setLevel(
            logging.DEBUG if settings.DEBUG else logging.INFO
        )
        self._logger.propagate = False

        # Avoid duplicate handlers
        if self._logger.handlers:
            return

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler (INFO and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        file_handler = RotatingFileHandler(
            filename=log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
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
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self._logger.addHandler(error_handler)

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        if self._logger is None:
            self._setup_logger()
        return self._logger


app_logger = AppLogger()
logger = app_logger.get_logger()


def get_logger(name: str = "tictactoe") -> logging.Logger:

    return logging.getLogger(name)

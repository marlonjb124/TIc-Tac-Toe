"""
Custom exceptions for the application.

"""

from typing import Any, Optional


class TicTacToeException(Exception):
    """Base exception class for all application exceptions."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

"""
Custom exceptions for the application.
Provides HTTP-specific exceptions following REST best practices.
"""

from typing import Any, Optional


class AppException(Exception):
    """Base exception class for all application exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize application exception.

        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Optional application-specific error code
            details: Optional additional error details
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize not found exception with 404 status code."""
        super().__init__(
            message=message,
            status_code=404,
            error_code=error_code,
            details=details,
        )


class ConflictException(AppException):
    """Exception raised when there's a conflict (e.g., duplicate resource)."""

    def __init__(
        self,
        message: str = "Resource already exists",
        error_code: str = "CONFLICT",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize conflict exception with 409 status code."""
        super().__init__(
            message=message,
            status_code=409,
            error_code=error_code,
            details=details,
        )


class UnauthorizedException(AppException):
    """Exception raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: str = "UNAUTHORIZED",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize unauthorized exception with 401 status code."""
        super().__init__(
            message=message,
            status_code=401,
            error_code=error_code,
            details=details,
        )


class ForbiddenException(AppException):
    """Exception raised when user lacks required permissions."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        error_code: str = "FORBIDDEN",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize forbidden exception with 403 status code."""
        super().__init__(
            message=message,
            status_code=403,
            error_code=error_code,
            details=details,
        )


class BadRequestException(AppException):
    """Exception raised when request validation fails."""

    def __init__(
        self,
        message: str = "Invalid request",
        error_code: str = "BAD_REQUEST",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize bad request exception with 400 status code."""
        super().__init__(
            message=message,
            status_code=400,
            error_code=error_code,
            details=details,
        )


# Game-specific exceptions


class InvalidMoveException(AppException):
    """Exception raised when a move is invalid."""

    def __init__(
        self,
        message: str = "Invalid move",
        error_code: str = "INVALID_MOVE",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize invalid move exception with 400 status code."""
        super().__init__(
            message=message,
            status_code=400,
            error_code=error_code,
            details=details,
        )


class GameOverException(AppException):
    """Exception raised when trying to play on a finished game."""

    def __init__(
        self,
        message: str = "Game is already finished",
        error_code: str = "GAME_OVER",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize game over exception with 400 status code."""
        super().__init__(
            message=message,
            status_code=400,
            error_code=error_code,
            details=details,
        )


class AIServiceException(AppException):
    """Exception raised when AI service fails."""

    def __init__(
        self,
        message: str = "AI service error",
        error_code: str = "AI_SERVICE_ERROR",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize AI service exception with 503 status code."""
        super().__init__(
            message=message,
            status_code=503,
            error_code=error_code,
            details=details,
        )

"""
Application configuration using Pydantic Settings.
Follows the FastAPI official template pattern.
"""

import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    """Parse CORS origins from string or list."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Tic-Tac-Toe API"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 600  # 10 hours default
    ALGORITHM: str = "HS256"

    # Environment
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    DEBUG: bool = False
    DEBUG: bool = True  # Show detailed errors in development

    # CORS
    FRONTEND_HOST: str = "http://localhost:5173"
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        """Get all CORS origins including frontend."""
        return [
            str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS
        ] + [self.FRONTEND_HOST]

    # Database - MariaDB/MySQL
    MYSQL_SERVER: str = "localhost"
    MYSQL_PORT: int = 33060  # Default to external port for local dev
    MYSQL_USER: str = "tictactoe_user"
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = "tictactoe"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Build database URI for MariaDB/MySQL with aiomysql."""
        return MultiHostUrl.build(
            scheme="mysql+aiomysql",
            username=self.MYSQL_USER,
            password=self.MYSQL_PASSWORD,
            host=self.MYSQL_SERVER,
            port=self.MYSQL_PORT,
            path=self.MYSQL_DB,
        ).unicode_string()

    FIRST_SUPERUSER: EmailStr = "admin@tictactoe.com"  # type: ignore
    FIRST_SUPERUSER_PASSWORD: str = "changethis123"

    # OpenRouter API Keys - Multiple keys for rotation
    OPENROUTER_API_KEYS: str = ""  # Comma-separated list of keys
    OPENROUTER_MODEL: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    AI_MAX_RETRIES: int = 3
    AI_TIMEOUT_SECONDS: int = 30

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_SIGNUP: str = "3/minute"
    RATE_LIMIT_AI_MOVE: str = "30/minute"

    @computed_field  # type: ignore
    @property
    def api_keys_list(self) -> list[str]:
        """Parse comma-separated API keys into a list."""
        if not self.OPENROUTER_API_KEYS:
            return []
        return [
            key.strip()
            for key in self.OPENROUTER_API_KEYS.split(",")
            if key.strip()
        ]

    @model_validator(mode="after")
    def _check_default_secret(self) -> Self:
        """Check if default secret is being used in production."""
        if self.ENVIRONMENT != "local":
            if self.SECRET_KEY == secrets.token_urlsafe(32):
                warnings.warn(
                    "Using default SECRET_KEY in non-local environment",
                    stacklevel=1,
                )
            if self.FIRST_SUPERUSER_PASSWORD == "changethis123":
                warnings.warn(
                    "Using default superuser password in production",
                    stacklevel=1,
                )
        return self


settings = Settings()  # type: ignore

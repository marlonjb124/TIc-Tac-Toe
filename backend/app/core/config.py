"""
Application configuration using Pydantic Settings.

"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with validation.

    This class uses Pydantic Settings to manage configuration
    from environment variables. All settings are validated at startup
    """

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Tic-Tac-Toe API"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database Configuration
    DATABASE_URL: str = Field(
        default="mysql+aiomysql://user:password@localhost:3306/tictactoe",
        description="Database connection URL",
    )
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_USER: str = "tictactoe_user"
    DATABASE_PASSWORD: str = Field(default="", description="Database password")
    DATABASE_NAME: str = "tictactoe"

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        min_length=32,
        description="Secret key for JWT token generation",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )

    # AI Configuration
    OPENAI_API_KEY: Optional[str] = Field(
        default=None, description="OpenAI API key for AI opponent"
    )
    AI_MODEL: str = "gpt-4"
    AI_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0)

    # Environment
    ENVIRONMENT: str = Field(
        default="development", pattern="^(development|staging|production)$"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """
        Parse CORS origins from string or list.

        Args:
            v: CORS origins as string (JSON) or list

        Returns:
            List of CORS origins
        """
        if isinstance(v, str):
            import json

            return json.loads(v)
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"


# Singleton instance
settings = Settings()

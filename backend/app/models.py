"""Data models and schemas for the Tic-Tac-Toe API."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class GameStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    DRAW = "draw"


class Player(str, Enum):
    X = "X"
    O = "O"  # noqa: E741


class Difficulty(str, Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=100)


class UserUpdate(SQLModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=100)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    is_superuser: bool = False


class UserPublic(UserBase):
    id: int
    created_at: datetime
    is_superuser: bool = False


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: Optional[int] = None
    exp: Optional[int] = None


# ===== Game Models =====


# Shared properties for Game
class GameBase(SQLModel):
    """Base game properties shared across schemas."""

    difficulty: Difficulty = Field(
        default=Difficulty.MEDIUM,
        description="Difficulty level: 'EASY', 'MEDIUM', or 'HARD'",
    )


# Properties to receive via API on game creation
class GameCreate(GameBase):
    """Schema for game creation via API."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"difficulty": "MEDIUM"},
                {"difficulty": "HARD"},
                {"difficulty": "EASY"},
            ]
        }
    }


# Database model for Game
class Game(GameBase, table=True):
    """Game database model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    board: str = Field(default=" " * 9, max_length=9)  # 9 positions (0-8)
    status: GameStatus = Field(default=GameStatus.IN_PROGRESS)
    current_player: Player = Field(default=Player.X)
    winner: Optional[Player] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# Properties to return via API
class GamePublic(GameBase):
    """Public game properties returned via API."""

    id: int
    user_id: int
    board: list[str]  # Return as array for frontend
    status: GameStatus
    current_player: Player
    winner: Optional[Player]
    created_at: datetime
    updated_at: datetime


class GamesPublic(SQLModel):
    """Paginated list of games."""

    data: list[GamePublic]
    count: int


# Move models
class MoveCreate(SQLModel):
    """Schema for creating a move."""

    position: int = Field(
        ge=0,
        le=8,
        description="Board position (0-8). Layout: 0|1|2 / 3|4|5 / 6|7|8",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{"position": 0}, {"position": 4}, {"position": 8}]
        }
    }


class MovePublic(SQLModel):
    """Public move information."""

    position: int
    player: Player
    board: list[str]
    status: GameStatus
    winner: Optional[Player]
    ai_move: Optional[int] = None  # AI's response move position


# Database model for Move (optional, for history tracking)
class Move(SQLModel, table=True):
    """Move database model for tracking game history."""

    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.id", index=True)
    position: int = Field(ge=0, le=8)
    player: Player
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# User Statistics Models
class UserStats(SQLModel):

    total_games: int = 0
    games_in_progress: int = 0
    games_finished: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    win_rate: float = 0.0  # Percentage of wins from finished games

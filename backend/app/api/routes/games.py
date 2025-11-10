"""Game endpoints for Tic-Tac-Toe API."""

from typing import Any, Optional

from fastapi import APIRouter, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.models import GameCreate, GamePublic, MoveCreate, MovePublic
from app.services.game_service import game_service

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/",
    response_model=GamePublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create new game",
    description="""
    Create a new Tic-Tac-Toe game with AI or algorithm opponent.

    **Opponent Types:**
    - `ai`: Uses OpenRouter API for intelligent gameplay
    - `algorithm`: Uses local minimax algorithm


    **Difficulty Levels:**
    - `EASY`: Casual play, makes occasional mistakes
    - `MEDIUM`: Strategic but not perfect (default)
    - `HARD`: Optimal play, never loses
    """,
)
async def create_game(
    session: SessionDep,
    current_user: CurrentUser,
    game_in: GameCreate,
) -> Any:
    return await game_service.create_game(
        session=session,
        user_id=current_user.id,
        game_create=game_in,
    )


@router.get(
    "/{game_id}",
    response_model=GamePublic,
    summary="Get game by ID",
)
async def get_game(
    session: SessionDep,
    current_user: CurrentUser,
    game_id: int,
) -> Any:
    return await game_service.get_game(
        session=session,
        game_id=game_id,
        user_id=current_user.id,
    )


@router.post(
    "/{game_id}/move",
    response_model=MovePublic,
    summary="Make a move",
    description="""
    Make a move in the Tic-Tac-Toe game.

    **Board Layout:**
    ```
    0 | 1 | 2
    ---------
    3 | 4 | 5
    ---------
    6 | 7 | 8
    ```

    The AI will automatically respond with its move.
    Returns the updated board state after both moves.
    """,
)
@limiter.limit(settings.RATE_LIMIT_AI_MOVE)
async def make_move(
    request: Request,
    session: SessionDep,
    current_user: CurrentUser,
    game_id: int,
    move_in: MoveCreate,
) -> Any:
    return await game_service.make_move(
        session=session,
        game_id=game_id,
        user_id=current_user.id,
        move_create=move_in,
    )


@router.get(
    "/",
    response_model=list[GamePublic],
    summary="List user's games",
    description="""
    Get list of user's games with optional filtering.

    **Filter by status:**
    - `in_progress`: Only active games
    - `finished`: Only completed games (won/lost)
    - `draw`: Only tied games
    - No filter: All games

    Results are ordered by most recently updated first.
    """,
)
async def list_games(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
) -> Any:
    from app.models import GameStatus

    game_status = None
    if status:
        try:
            game_status = GameStatus(status)
        except ValueError:
            pass

    return await game_service.list_games(
        session=session,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=game_status,
    )

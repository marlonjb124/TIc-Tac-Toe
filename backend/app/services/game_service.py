"""
Game service for Tic-Tac-Toe business logic.
"""

from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.exceptions import (
    GameOverException,
    InvalidMoveException,
    NotFoundException,
)
from app.core.game_engine import GameEngine
from app.models import (
    Game,
    GameCreate,
    GamePublic,
    GameStatus,
    Move,
    MoveCreate,
    MovePublic,
    OpponentType,
    Player,
)
from app.services.ai_service import ai_service


class GameService:
    """Manages game operations and AI interactions."""

    async def create_game(
        self,
        session: AsyncSession,
        user_id: int,
        game_create: GameCreate,
    ) -> GamePublic:
        """Start a new game session."""
        game_data = game_create.model_dump()
        game = Game(
            **game_data,
            user_id=user_id,
            board=" " * 9,
            status=GameStatus.IN_PROGRESS,
            current_player=Player.X,
        )

        session.add(game)
        await session.commit()
        await session.refresh(game)

        return self._to_public(game)

    async def get_game(
        self, session: AsyncSession, game_id: int, user_id: int
    ) -> GamePublic:
        """Fetch game details for the user."""
        statement = select(Game).where(
            Game.id == game_id, Game.user_id == user_id
        )
        result = await session.execute(statement)
        game = result.scalar_one_or_none()

        if not game:
            raise NotFoundException(
                message=f"Game with id {game_id} not found",
                details={"game_id": game_id},
            )

        return self._to_public(game)

    async def make_move(
        self,
        session: AsyncSession,
        game_id: int,
        user_id: int,
        move_create: MoveCreate,
    ) -> MovePublic:
        """Process player move and trigger AI response."""
        statement = select(Game).where(
            Game.id == game_id, Game.user_id == user_id
        )
        result = await session.execute(statement)
        game = result.scalar_one_or_none()

        if not game:
            raise NotFoundException(
                message=f"Game with id {game_id} not found",
                details={"game_id": game_id},
            )

        if game.status != GameStatus.IN_PROGRESS:
            raise GameOverException(
                message="Game is already finished",
                details={"status": game.status, "winner": game.winner},
            )

        # Validate move
        if not GameEngine.is_valid_move(game.board, move_create.position):
            raise InvalidMoveException(
                message=f"Position {move_create.position} is not available",
                details={
                    "position": move_create.position,
                    "board": GameEngine.board_to_list(game.board),
                },
            )

        game.board = GameEngine.make_move(
            game.board, move_create.position, Player.X
        )

        session.add(
            Move(
                game_id=game.id,
                position=move_create.position,
                player=Player.X,
            )
        )

        winner = GameEngine.check_winner(game.board)
        if winner:
            game.status = GameStatus.FINISHED
            game.winner = winner
            await session.commit()
            await session.refresh(game)

            return MovePublic(
                position=move_create.position,
                player=Player.X,
                board=GameEngine.board_to_list(game.board),
                status=game.status,
                winner=game.winner,
            )

        if GameEngine.is_board_full(game.board):
            game.status = GameStatus.DRAW
            await session.commit()
            await session.refresh(game)

            return MovePublic(
                position=move_create.position,
                player=Player.X,
                board=GameEngine.board_to_list(game.board),
                status=game.status,
                winner=None,
            )

        ai_position: Optional[int] = None

        if game.opponent_type == OpponentType.AI:
            # TODO: Add timeout handling for AI requests
            ai_position = await ai_service.get_move(
                board=game.board,
                player=Player.O,
                difficulty=game.difficulty,
            )

            game.board = GameEngine.make_move(
                game.board, ai_position, Player.O
            )

            session.add(
                Move(
                    game_id=game.id,
                    position=ai_position,
                    player=Player.O,
                )
            )

            winner = GameEngine.check_winner(game.board)
            if winner:
                game.status = GameStatus.FINISHED
                game.winner = winner
            elif GameEngine.is_board_full(game.board):
                game.status = GameStatus.DRAW

        await session.commit()
        await session.refresh(game)

        return MovePublic(
            position=move_create.position,
            player=Player.X,
            board=GameEngine.board_to_list(game.board),
            status=game.status,
            winner=game.winner,
            ai_move=ai_position,
        )

    async def list_games(
        self,
        session: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[GamePublic]:
        """Get user's game history."""
        statement = (
            select(Game)
            .where(Game.user_id == user_id)
            .order_by(Game.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(statement)
        games = result.scalars().all()

        return [self._to_public(game) for game in games]

    def _to_public(self, game: Game) -> GamePublic:
        game_dict = game.model_dump()
        game_dict["board"] = GameEngine.board_to_list(game.board)
        return GamePublic(**game_dict)


game_service = GameService()

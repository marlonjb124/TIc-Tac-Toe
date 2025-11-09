"""
Game engine for Tic-Tac-Toe logic.
Implements game rules, validation, and win condition checking.
Follows Single Responsibility Principle (SOLID).
"""

from typing import Optional

from app.models import Player


class GameEngine:
    """
    Handles core Tic-Tac-Toe game logic.

    Responsibilities:
    - Validate moves
    - Check win conditions
    - Detect draw conditions
    - Manage board state
    """

    # Win combinations (rows, columns, diagonals)
    WIN_COMBINATIONS = [
        [0, 1, 2],  # Top row
        [3, 4, 5],  # Middle row
        [6, 7, 8],  # Bottom row
        [0, 3, 6],  # Left column
        [1, 4, 7],  # Middle column
        [2, 5, 8],  # Right column
        [0, 4, 8],  # Diagonal \
        [2, 4, 6],  # Diagonal /
    ]

    @staticmethod
    def is_valid_move(board: str, position: int) -> bool:
        """
        Validate if a move is legal.

        Args:
            board: Current board state (9-character string)
            position: Position to check (0-8)

        Returns:
            True if move is valid, False otherwise
        """
        if position < 0 or position > 8:
            return False

        return board[position] == " "

    @staticmethod
    def make_move(board: str, position: int, player: Player) -> str:
        """
        Apply a move to the board.

        Args:
            board: Current board state
            position: Position to place mark (0-8)
            player: Player making the move (X or O)

        Returns:
            New board state after move
        """
        board_list = list(board)
        board_list[position] = player.value
        return "".join(board_list)

    @staticmethod
    def check_winner(board: str) -> Optional[Player]:
        """
        Check if there's a winner.

        Args:
            board: Current board state

        Returns:
            Winning player (X or O) or None if no winner
        """
        for combo in GameEngine.WIN_COMBINATIONS:
            positions = [board[i] for i in combo]

            # Check if all three positions have the same non-empty mark
            if (
                positions[0] != " "
                and positions[0] == positions[1] == positions[2]
            ):
                return Player(positions[0])

        return None

    @staticmethod
    def is_board_full(board: str) -> bool:
        """
        Check if board is completely filled.

        Args:
            board: Current board state

        Returns:
            True if board is full, False otherwise
        """
        return " " not in board

    @staticmethod
    def get_available_moves(board: str) -> list[int]:
        """
        Get list of available positions.

        Args:
            board: Current board state

        Returns:
            List of available position indices
        """
        return [i for i, cell in enumerate(board) if cell == " "]

    @staticmethod
    def board_to_list(board: str) -> list[str]:
        """
        Convert board string to list for API response.

        Args:
            board: Board state as string

        Returns:
            Board as list of strings
        """
        return list(board)

    @staticmethod
    def get_opponent(player: Player) -> Player:
        """
        Get the opposing player.

        Args:
            player: Current player

        Returns:
            Opponent player
        """
        return Player.O if player == Player.X else Player.X

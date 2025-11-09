"""
AI Service for Tic-Tac-Toe opponent using OpenRouter API.
Implements Dependency Inversion Principle (SOLID).
"""

import httpx

from app.core.config import settings
from app.core.exceptions import AIServiceException
from app.models import Difficulty, Player


class AIService:
    """
    Service for AI-powered Tic-Tac-Toe opponent.
    Uses OpenRouter API to generate intelligent moves based on board state.
    """

    def __init__(self) -> None:
        """Initialize AI service with configuration."""
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.base_url = settings.OPENROUTER_BASE_URL
        self.max_retries = settings.AI_MAX_RETRIES
        self.timeout = settings.AI_TIMEOUT_SECONDS

    async def get_move(
        self,
        board: str,
        player: Player,
        difficulty: Difficulty = Difficulty.MEDIUM,
    ) -> int:
        """
        Get AI's next move for the current board state.

        Args:
            board: Current board state (9-character string)
            player: AI's player marker (X or O)
            difficulty: Difficulty level (easy, medium, hard)

        Returns:
            Position index (0-8) for AI's move

        Raises:
            AIServiceException: If AI service fails or returns invalid move
        """
        if not self.api_key:
            raise AIServiceException(
                message="OpenRouter API key not configured",
                details={"config": "OPENROUTER_API_KEY is required"},
            )

        prompt = self._build_prompt(board, player, difficulty)

        for attempt in range(self.max_retries):
            try:
                move = await self._call_api(prompt)

                # Validate the move
                if self._is_valid_move(board, move):
                    return move
                else:
                    # If invalid, try again
                    if attempt < self.max_retries - 1:
                        continue
                    raise AIServiceException(
                        message="AI returned invalid move after retries",
                        details={"move": move, "board": board},
                    )

            except httpx.HTTPError as e:
                if attempt < self.max_retries - 1:
                    continue
                raise AIServiceException(
                    message="Failed to get AI response",
                    details={"error": str(e), "attempt": attempt + 1},
                )

        raise AIServiceException(
            message="Max retries exceeded",
            details={"retries": self.max_retries},
        )

    def _build_prompt(
        self, board: str, player: Player, difficulty: Difficulty
    ) -> str:
        """
        Build prompt for AI model.

        Args:
            board: Current board state
            player: AI's player marker
            difficulty: Difficulty level

        Returns:
            Formatted prompt string
        """
        board_visual = self._format_board_for_display(board)
        opponent = "X" if player == Player.O else "O"

        # Get available positions
        available = [str(i) for i, cell in enumerate(board) if cell == " "]
        available_str = ", ".join(available)

        difficulty_instructions = {
            Difficulty.EASY: (
                "Play casually. Prioritize random moves over strategy. "
                "Only block obvious wins occasionally."
            ),
            Difficulty.MEDIUM: (
                "Play strategically. Block opponent wins and take your "
                "own winning moves when available, but don't plan ahead "
                "more than one move."
            ),
            Difficulty.HARD: (
                "Play optimally using perfect strategy. Never lose. "
                "Always think several moves ahead."
            ),
        }

        instruction = difficulty_instructions.get(
            difficulty, difficulty_instructions[Difficulty.MEDIUM]
        )

        player_mark = player.value

        prompt = f"""You are an expert Tic-Tac-Toe player. \
You are '{player_mark}'.

CURRENT BOARD:
{board_visual}

AVAILABLE POSITIONS: {available_str}
(You can ONLY choose from these empty positions)

POSITION REFERENCE:
0 | 1 | 2
---------
3 | 4 | 5
---------
6 | 7 | 8

WINNING COMBINATIONS:
Rows: [0,1,2], [3,4,5], [6,7,8]
Columns: [0,3,6], [1,4,7], [2,5,8]
Diagonals: [0,4,8], [2,4,6]

STRATEGY RULES (Priority Order):
1. WIN: If you have 2 in a row, take the winning position
2. BLOCK: If opponent '{opponent}' has 2 in a row, block them
3. FORK: Create two winning threats at once
4. BLOCK FORK: Prevent opponent from creating a fork
5. CENTER: Take center (4) if available - strongest position
6. OPPOSITE CORNER: If opponent is in a corner, take opposite corner
7. EMPTY CORNER: Take any corner (0,2,6,8)
8. EMPTY SIDE: Take any side (1,3,5,7)

EXAMPLES:
- Board "X X  O    " → You MUST play position 2 to WIN [0,1,2]
- Board "O X X     " → You MUST play position 0 to BLOCK [0,1,2]
- Board "X   O   X" → You MUST play position 4 to BLOCK diagonal
- Board "         " → Play position 4 (center) - best first move
- Board "X        " → Play position 4 (center) or corner (2,6,8)

DIFFICULTY: {difficulty.value}
INSTRUCTIONS: {instruction}

ANALYZE the current board state carefully:
- Check for immediate winning moves
- Check if opponent can win next turn (MUST BLOCK)
- Look for fork opportunities
- Consider center and corner positions

Respond with ONLY ONE NUMBER (0-8) - no text, no explanation.

Your move:"""

        return prompt

    def _format_board_for_display(self, board: str) -> str:
        """Format board as visual grid for AI."""
        b = list(board)
        return f"""{b[0]} | {b[1]} | {b[2]}
---------
{b[3]} | {b[4]} | {b[5]}
---------
{b[6]} | {b[7]} | {b[8]}"""

    async def _call_api(self, prompt: str) -> int:
        """
        Call OpenRouter API and parse response.

        Args:
            prompt: Formatted prompt for AI

        Returns:
            Move position (0-8)

        Raises:
            AIServiceException: If API call fails or response is invalid
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0.7,
            "max_tokens": 10,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

            data = response.json()

            # Extract move from response
            try:
                print(data)
                content = data["choices"][0]["message"]["content"].strip()
                print(content)
                # Try to extract number from response
                move = int(content)
                return move
            except (KeyError, ValueError, IndexError) as e:
                raise AIServiceException(
                    message="Failed to parse AI response",
                    details={
                        "response": data,
                        "error": str(e),
                    },
                )

    def _is_valid_move(self, board: str, move: int) -> bool:
        """
        Validate if move is legal.

        Args:
            board: Current board state
            move: Position to check

        Returns:
            True if valid, False otherwise
        """
        if move < 0 or move > 8:
            return False
        return board[move] == " "


# Singleton instance
ai_service = AIService()

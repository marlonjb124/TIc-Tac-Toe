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
    With automatic API key rotation to handle rate limits.
    """

    def __init__(self) -> None:
        """Initialize AI service with configuration."""
        self.api_keys = settings.api_keys_list
        self.current_key_index = 0
        self.model = settings.OPENROUTER_MODEL
        self.base_url = settings.OPENROUTER_BASE_URL
        self.max_retries = settings.AI_MAX_RETRIES
        self.timeout = settings.AI_TIMEOUT_SECONDS

    def _get_next_api_key(self) -> str:
        """Get next API key in rotation."""
        if not self.api_keys:
            raise AIServiceException(
                message="No OpenRouter API keys configured",
                details={"config": "OPENROUTER_API_KEYS is required"},
            )

        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(
            self.api_keys
        )
        return key

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
        # FAST PATH: Check if AI can win immediately (before calling API)
        opponent_mark = "X" if player == Player.O else "O"
        player_mark = player.value
        quick_threats = self._analyze_threats(
            board, opponent_mark, player_mark
        )

        if quick_threats["you_can_win"]:
            winning_move = quick_threats["your_win_pos"]
            print(
                f"⚡ INSTANT WIN detected at position {winning_move} - taking it without API call"
            )
            return winning_move

        prompt = self._build_prompt(board, player, difficulty)
        invalid_moves = []
        last_error = None

        for attempt in range(self.max_retries):
            try:
                # Update prompt with invalid moves from previous attempts
                if invalid_moves:
                    available = [
                        str(i)
                        for i in range(9)
                        if board[i] == " " and i not in invalid_moves
                    ]
                    prompt += f"\n\nWARNING: Positions {invalid_moves} are INVALID or already taken. You MUST choose from: {', '.join(available)}"

                move = await self._call_api(prompt, board)
                print(f"AI attempt {attempt + 1}: move={move}")

                # Validate the move
                if self._is_valid_move(board, move):
                    return move
                else:
                    # Track invalid move and try again
                    invalid_moves.append(move)
                    if attempt < self.max_retries - 1:
                        print(
                            f"Invalid move {move}, retrying with updated prompt..."
                        )
                        continue
                    raise AIServiceException(
                        message="AI returned invalid move after retries",
                        details={
                            "move": move,
                            "board": board,
                            "invalid_attempts": invalid_moves,
                        },
                    )

            except httpx.HTTPStatusError as e:
                last_error = e
                print(
                    f"API call failed (attempt {attempt + 1}): "
                    f"{e.response.status_code} - Rotating to next key..."
                )
                if attempt < self.max_retries - 1:
                    continue
                raise AIServiceException(
                    message="Failed to get AI response",
                    details={
                        "error": str(e),
                        "status_code": e.response.status_code,
                        "attempt": attempt + 1,
                    },
                )
            except httpx.HTTPError as e:
                last_error = e
                print(f"HTTP error (attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries - 1:
                    continue
                raise AIServiceException(
                    message="Failed to get AI response",
                    details={"error": str(e), "attempt": attempt + 1},
                )

        raise AIServiceException(
            message="Max retries exceeded",
            details={
                "retries": self.max_retries,
                "last_error": str(last_error) if last_error else None,
            },
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
                "Play casually with some mistakes. "
                "You should still block obvious wins 50% of the time."
            ),
            Difficulty.MEDIUM: (
                "Play competitively. ALWAYS block opponent wins. "
                "ALWAYS take your own winning moves. "
                "Use basic strategy but don't plan too far ahead."
            ),
            Difficulty.HARD: (
                "Play perfectly. NEVER miss a block. NEVER miss a win. "
                "Use optimal minimax strategy. Think 3+ moves ahead."
            ),
        }

        instruction = difficulty_instructions.get(
            difficulty, difficulty_instructions[Difficulty.MEDIUM]
        )

        player_mark = player.value

        # Check for immediate threats
        threats = self._analyze_threats(board, opponent, player_mark)
        threat_warning = ""

        # PRIORITY 1: If AI can win, emphasize it FIRST (most important)
        if threats["you_can_win"]:
            threat_warning = f"\n🎯 WINNING MOVE AVAILABLE: Position {threats['your_win_pos']} wins the game! TAKE IT NOW!"
            # Add block warning as secondary if both exist
            if threats["opponent_can_win"]:
                threat_warning += f"\n(Note: Opponent also threatens position {threats['opponent_win_pos']}, but WIN takes priority)"
        # PRIORITY 2: If only opponent can win, block it
        elif threats["opponent_can_win"]:
            threat_warning = f"\n⚠️ CRITICAL BLOCK: Opponent can WIN at position {threats['opponent_win_pos']}! YOU MUST BLOCK THIS!"

        prompt = f"""You are playing Tic-Tac-Toe as '{player_mark}' against '{opponent}'.

CURRENT BOARD:
{board_visual}

AVAILABLE POSITIONS: {available_str}
{threat_warning}

POSITION REFERENCE:
0 | 1 | 2
---------
3 | 4 | 5
---------
6 | 7 | 8

WINNING COMBINATIONS TO CHECK:
Rows: [0,1,2], [3,4,5], [6,7,8]
Cols: [0,3,6], [1,4,7], [2,5,8]
Diags: [0,4,8], [2,4,6]

MANDATORY RULES (CHECK IN ORDER):
1. ✓ WIN NOW: If you have 2 '{player_mark}' in any line, TAKE the 3rd position to WIN
2. ⚠️ BLOCK NOW: If opponent has 2 '{opponent}' in any line, BLOCK the 3rd position IMMEDIATELY
3. Center (4): Best position if available
4. Corners (0,2,6,8): Strong positions
5. Sides (1,3,5,7): Weakest positions

STEP-BY-STEP ANALYSIS:
1. Check ALL 8 winning combinations for 2 '{player_mark}' + 1 empty -> WIN there
2. Check ALL 8 winning combinations for 2 '{opponent}' + 1 empty -> BLOCK there
3. If neither, take center (4) or a corner

DIFFICULTY: {difficulty.value}
INSTRUCTIONS: {instruction}

Think carefully. Analyze the board. Then respond with ONLY ONE NUMBER (0-8).

Your move:"""

        return prompt

    def _analyze_threats(self, board: str, opponent: str, player: str) -> dict:
        """Analyze board for immediate threats and opportunities."""
        lines = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],  # Rows
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],  # Cols
            [0, 4, 8],
            [2, 4, 6],  # Diagonals
        ]

        result = {
            "opponent_can_win": False,
            "opponent_win_pos": None,
            "you_can_win": False,
            "your_win_pos": None,
        }

        for line in lines:
            cells = [board[i] for i in line]

            # Check if opponent can win
            if cells.count(opponent) == 2 and cells.count(" ") == 1:
                result["opponent_can_win"] = True
                result["opponent_win_pos"] = line[cells.index(" ")]

            # Check if AI can win
            if cells.count(player) == 2 and cells.count(" ") == 1:
                result["you_can_win"] = True
                result["your_win_pos"] = line[cells.index(" ")]

        return result

    def _format_board_for_display(self, board: str) -> str:
        """Format board as visual grid for AI."""
        b = list(board)
        return f"""{b[0]} | {b[1]} | {b[2]}
---------
{b[3]} | {b[4]} | {b[5]}
---------
{b[6]} | {b[7]} | {b[8]}"""

    async def _call_api(self, prompt: str, board: str) -> int:
        """
        Call OpenRouter API and parse response.

        Args:
            prompt: Formatted prompt for AI
            board: Current board state for debugging

        Returns:
            Move position (0-8)

        Raises:
            AIServiceException: If API call fails or response is invalid
        """
        # Get next API key from rotation
        api_key = self._get_next_api_key()
        key_suffix = api_key[-8:] if len(api_key) > 8 else api_key
        print(f"Using API key ending in ...{key_suffix}")

        headers = {
            "Authorization": f"Bearer {api_key}",
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
            "max_tokens": 20,  # Increased from 10 to meet minimum of 16
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            print(f"Calling OpenRouter API: {self.base_url}/chat/completions")
            print(f"Model: {self.model}")
            print(f"Prompt length: {len(prompt)} characters")

            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )

            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")

            # Log response body before raising errors
            try:
                response_text = response.text
                print(
                    f"Response body: {response_text[:500]}..."
                )  # First 500 chars
            except Exception as e:
                print(f"Could not read response body: {e}")

            response.raise_for_status()

            data = response.json()
            print(f"Parsed JSON response: {data}")

            # Extract move from response
            try:
                content = data["choices"][0]["message"]["content"].strip()
                print(
                    f"AI Response: '{content}' (Key #{self.current_key_index})"
                )

                # Extract only the first digit found
                import re

                match = re.search(r"\d", content)
                if not match:
                    raise ValueError("No digit found in response")

                move = int(match.group())
                available = [i for i, c in enumerate(board) if c == " "]
                print(f"Parsed move: {move}, Available: {available}")
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

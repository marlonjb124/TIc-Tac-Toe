"""AI opponent for Tic-Tac-Toe using OpenRouter API."""

import httpx

from app.core.config import settings
from app.core.exceptions import AIServiceException
from app.core.logger import get_logger
from app.models import Difficulty, Player

logger = get_logger(__name__)


class AIService:
    def __init__(self) -> None:
        self.api_keys = settings.api_keys_list
        self.current_key_index = 0
        self.model = settings.OPENROUTER_MODEL
        self.base_url = settings.OPENROUTER_BASE_URL
        self.max_retries = settings.AI_MAX_RETRIES
        self.timeout = settings.AI_TIMEOUT_SECONDS

    def _get_next_api_key(self) -> str:
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
        opponent_mark = "X" if player == Player.O else "O"
        player_mark = player.value
        threats = self._analyze_threats(board, opponent_mark, player_mark)

        if threats["you_can_win"]:
            winning_pos = threats["your_win_pos"]
            logger.info(f"Instant win at {winning_pos} for {player.value}")
            return winning_pos

        prompt = self._build_prompt(board, player, difficulty)
        invalid_positions = []
        last_error = None

        for attempt in range(self.max_retries):
            try:
                if invalid_positions:
                    available = [
                        str(i)
                        for i in range(9)
                        if board[i] == " " and i not in invalid_positions
                    ]
                    prompt += f"\n\nWARNING: Positions {invalid_positions} are INVALID. Choose from: {', '.join(available)}"

                position = await self._call_api(prompt, board)
                logger.debug(f"AI attempt {attempt + 1}: position={position}")

                if self._is_valid_move(board, position):
                    logger.info(
                        f"AI selected position {position} (difficulty: {difficulty.value})"
                    )
                    return position
                else:
                    invalid_positions.append(position)
                    if attempt < self.max_retries - 1:
                        logger.warning(
                            f"Invalid position {position}, retrying..."
                        )
                        continue
                    raise AIServiceException(
                        message="AI returned invalid move after retries",
                        details={
                            "move": position,
                            "board": board,
                            "invalid_attempts": invalid_positions,
                        },
                    )

            except httpx.HTTPStatusError as e:
                last_error = e
                logger.error(
                    f"API {e.response.status_code} (attempt {attempt + 1}), rotating key..."
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
                logger.error(f"HTTP error (attempt {attempt + 1}): {str(e)}")
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
        board_visual = self._format_board_for_display(board)
        opponent = "X" if player == Player.O else "O"
        available = [str(i) for i, cell in enumerate(board) if cell == " "]
        available_str = ", ".join(available)

        difficulty_instructions = {
            Difficulty.EASY: "Play casually. Block obvious wins 50% of the time.",
            Difficulty.MEDIUM: "ALWAYS block opponent wins. ALWAYS take your wins. Use basic strategy.",
            Difficulty.HARD: "Play perfectly. NEVER miss blocks or wins. Think 3+ moves ahead.",
        }

        instruction = difficulty_instructions.get(
            difficulty, difficulty_instructions[Difficulty.MEDIUM]
        )

        player_mark = player.value
        threats = self._analyze_threats(board, opponent, player_mark)
        threat_warning = ""

        if threats["you_can_win"]:
            threat_warning = f"\n🎯 WINNING MOVE AVAILABLE: Position {threats['your_win_pos']} wins the game! TAKE IT NOW!"
            if threats["opponent_can_win"]:
                threat_warning += f"\n(Note: Opponent also threatens position {threats['opponent_win_pos']}, but WIN takes priority)"
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
        lines = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 8],
            [2, 4, 6],
        ]

        result = {
            "opponent_can_win": False,
            "opponent_win_pos": None,
            "you_can_win": False,
            "your_win_pos": None,
        }

        for line in lines:
            cells = [board[i] for i in line]

            if cells.count(opponent) == 2 and cells.count(" ") == 1:
                result["opponent_can_win"] = True
                result["opponent_win_pos"] = line[cells.index(" ")]

            if cells.count(player) == 2 and cells.count(" ") == 1:
                result["you_can_win"] = True
                result["your_win_pos"] = line[cells.index(" ")]

        return result

    def _format_board_for_display(self, board: str) -> str:
        b = list(board)
        return f"""{b[0]} | {b[1]} | {b[2]}
---------
{b[3]} | {b[4]} | {b[5]}
---------
{b[6]} | {b[7]} | {b[8]}"""

    async def _call_api(self, prompt: str, board: str) -> int:
        api_key = self._get_next_api_key()
        key_suffix = api_key[-8:] if len(api_key) > 8 else api_key
        logger.debug(f"Using API key ...{key_suffix}")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 20,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            logger.debug(f"Calling {self.base_url}/chat/completions")
            logger.debug(f"Model: {self.model}, Prompt: {len(prompt)} chars")

            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )

            logger.debug(f"Response status: {response.status_code}")

            try:
                response_text = response.text
                logger.debug(f"Response: {response_text[:500]}...")
            except Exception as e:
                logger.warning(f"Could not read response: {e}")

            response.raise_for_status()

            json_response = response.json()
            logger.debug(f"Parsed JSON: {json_response}")

            try:
                content = json_response["choices"][0]["message"][
                    "content"
                ].strip()
                logger.debug(
                    f"AI response: '{content}' (Key #{self.current_key_index})"
                )

                import re

                match = re.search(r"\d", content)
                if not match:
                    raise ValueError("No digit in response")

                position = int(match.group())
                available = [i for i, c in enumerate(board) if c == " "]
                logger.debug(f"Parsed: {position}, Available: {available}")
                return position
            except (KeyError, ValueError, IndexError) as e:
                logger.error(f"Failed to parse response: {str(e)}")
                raise AIServiceException(
                    message="Failed to parse AI response",
                    details={"response": json_response, "error": str(e)},
                )

    def _is_valid_move(self, board: str, position: int) -> bool:
        if position < 0 or position > 8:
            return False
        return board[position] == " "


ai_service = AIService()

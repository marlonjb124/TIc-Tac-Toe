import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useCreateGame, useMakeMove, useCurrentUser } from "../hooks/useApi";
import { gameApi } from "../api";
import Board from "../components/Board";
import type { Difficulty, MoveResponse } from "../types";

export default function GamePage() {
  const [searchParams] = useSearchParams();
  const existingGameId = searchParams.get("id");

  const [gameId, setGameId] = useState<number | null>(
    existingGameId ? parseInt(existingGameId) : null
  );
  const [board, setBoard] = useState<string[]>(Array(9).fill(" "));
  const [gameStatus, setGameStatus] = useState<"in_progress" | "finished" | "draw">("in_progress");
  const [winner, setWinner] = useState<string | null>(null);
  const [difficulty, setDifficulty] = useState<Difficulty>("MEDIUM");
  const [lastMove, setLastMove] = useState<MoveResponse | null>(null);

  const navigate = useNavigate();
  const { data: user } = useCurrentUser();
  const createGameMutation = useCreateGame();
  const makeMoveMutation = useMakeMove(gameId || 0);

  // Load existing game if ID is in URL
  useEffect(() => {
    const loadGame = async () => {
      if (existingGameId) {
        try {
          const game = await gameApi.getGame(parseInt(existingGameId));
          setGameId(game.id);
          setBoard(game.board);
          setGameStatus(game.status);
          setWinner(game.winner);
          setDifficulty(game.difficulty);
        } catch (error) {
          console.error("Failed to load game:", error);
          navigate("/dashboard");
        }
      }
    };
    loadGame();
  }, [existingGameId, navigate]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  const resetToMenu = () => {
    setGameId(null);
    setBoard(Array(9).fill(" "));
    setGameStatus("in_progress");
    setWinner(null);
    setLastMove(null);
  };

  const startNewGame = async () => {
    try {
      const game = await createGameMutation.mutateAsync({
        difficulty,
      });
      console.log("Game created:", game);
      setGameId(game.id);
      setBoard(game.board);
      setGameStatus("in_progress");
      setWinner(null);
      setLastMove(null);
    } catch (error) {
      console.error("Failed to create game:", error);
    }
  };

  const handleCellClick = async (position: number) => {
    if (!gameId || gameStatus !== "in_progress") return;

    // Immediately update board with player's move (optimistic update)
    const newBoard = [...board];
    newBoard[position] = "X";
    setBoard(newBoard);

    try {
      const moveResult = await makeMoveMutation.mutateAsync({ position });
      console.log("Move result:", moveResult);

      // Update with the complete board (including AI move)
      setBoard(moveResult.board);
      setGameStatus(moveResult.status);
      setWinner(moveResult.winner);
      setLastMove(moveResult);
    } catch (error) {
      console.error("Move failed:", error);
      // Revert optimistic update on error
      setBoard(board);
    }
  };

  const renderGameStatus = () => {
    if (gameStatus === "finished") {
      return (
        <div className={`text-3xl font-bold ${winner === "X" ? "text-green-400" : "text-red-400"}`}>
          {winner === "X" ? "You Win! 🎉" : "AI Wins! 🤖"}
        </div>
      );
    }
    if (gameStatus === "draw") {
      return <div className="text-3xl font-bold text-yellow-300">It's a Draw! 🤝</div>;
    }

    // Show AI's turn when request is pending
    if (makeMoveMutation.isPending) {
      return (
        <div className="text-2xl font-semibold text-purple-300 flex items-center gap-2">
          <span className="animate-pulse">🤖 AI is thinking...</span>
        </div>
      );
    }

    return <div className="text-2xl font-semibold text-white">Your turn (X)</div>;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 flex flex-col p-4">
      {/* Header */}
      <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl p-4 mb-4 border border-white/20">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-6">
            <div>
              <h1 className="text-3xl font-bold text-white">Tic-Tac-Toe</h1>
              <p className="text-white/70 text-sm">{user?.email}</p>
            </div>
            {gameId && (
              <div className="flex items-center gap-4 pl-6 border-l border-white/30">
                <div className="text-center">
                  <p className="text-white/60 text-xs uppercase tracking-wide">Difficulty</p>
                  <p className="text-white font-bold">
                    {difficulty === "EASY" && "🟢 Easy"}
                    {difficulty === "MEDIUM" && "🟡 Medium"}
                    {difficulty === "HARD" && "🔴 Hard"}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-white/60 text-xs uppercase tracking-wide">Status</p>
                  <p className="text-white font-bold">
                    {gameStatus === "in_progress" && "🎮 Playing"}
                    {gameStatus === "finished" && (winner === "X" ? "🎉 You Won!" : "🤖 AI Won")}
                    {gameStatus === "draw" && "🤝 Draw"}
                  </p>
                </div>
              </div>
            )}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate("/dashboard")}
              className="px-5 py-2 bg-white/20 backdrop-blur text-white rounded-xl hover:bg-white/30 transition-all border border-white/30 font-medium"
            >
              ← Dashboard
            </button>
            {gameId && (
              <button
                onClick={resetToMenu}
                className="px-5 py-2 bg-gradient-to-r from-green-400 to-emerald-500 text-white rounded-xl hover:from-green-500 hover:to-emerald-600 transition-all font-semibold shadow-lg transform hover:scale-105"
              >
                🔄 New Game
              </button>
            )}
            <button
              onClick={handleLogout}
              className="px-5 py-2 bg-white/20 backdrop-blur text-white rounded-xl hover:bg-white/30 transition-all border border-white/30 font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Game Area */}
      <div className="flex-1 flex items-center justify-center py-8">
        <div className="w-full max-w-2xl flex flex-col gap-8">
          <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl p-8 border border-white/20">
            {!gameId ? (
              <div className="text-center space-y-8">
                <div>
                  <h2 className="text-3xl font-bold text-white mb-2">Ready to Play?</h2>
                  <p className="text-white/70">Choose your difficulty and start the game</p>
                </div>

                <div className="flex flex-col items-center space-y-4 bg-gradient-to-br from-purple-500/30 to-pink-500/30 p-6 rounded-xl">
                  <span className="text-white font-semibold text-lg">Difficulty Level</span>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value as Difficulty)}
                    className="w-64 px-4 py-3 bg-white/30 backdrop-blur border border-white/40 rounded-xl text-white font-medium focus:ring-2 focus:ring-white/50 focus:outline-none text-center"
                  >
                    <option value="EASY" className="text-gray-900">🟢 Easy</option>
                    <option value="MEDIUM" className="text-gray-900">🟡 Medium</option>
                    <option value="HARD" className="text-gray-900">🔴 Hard</option>
                  </select>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Status */}
                <div className="text-center min-h-[60px] flex items-center justify-center">
                  {renderGameStatus()}
                </div>

                {/* Board */}
                <div className="flex justify-center">
                  <Board
                    board={board}
                    onCellClick={handleCellClick}
                    disabled={makeMoveMutation.isPending || gameStatus !== "in_progress"}
                    lastMove={lastMove}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Start Game Button */}
          {!gameId && (
            <div className="flex justify-center">
              <button
                onClick={startNewGame}
                disabled={createGameMutation.isPending}
                className="px-16 py-5 bg-gradient-to-r from-green-400 to-blue-500 text-white rounded-2xl hover:from-green-500 hover:to-blue-600 disabled:from-gray-400 disabled:to-gray-500 transition-all font-bold text-2xl shadow-2xl transform hover:scale-105 disabled:scale-100"
              >
                {createGameMutation.isPending ? "Creating..." : "🎮 Start Game"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

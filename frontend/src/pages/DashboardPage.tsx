import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { authApi, gameApi } from "../api";
import type { Game } from "../types";

export default function DashboardPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<string>("all");

  const { data: user } = useQuery({
    queryKey: ["currentUser"],
    queryFn: authApi.getCurrentUser,
  });

  const { data: stats } = useQuery({
    queryKey: ["userStats"],
    queryFn: authApi.getUserStats,
  });

  const { data: games } = useQuery({
    queryKey: ["games", filter],
    queryFn: () => gameApi.listGames(filter === "all" ? undefined : filter),
  });

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  const handleNewGame = () => {
    navigate("/game");
  };

  const handleContinueGame = (gameId: number) => {
    navigate(`/game?id=${gameId}`);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "in_progress":
        return (
          <span className="px-3 py-1 bg-yellow-500/20 text-yellow-200 rounded-full text-xs font-semibold">
            In Progress
          </span>
        );
      case "finished":
        return (
          <span className="px-3 py-1 bg-green-500/20 text-green-200 rounded-full text-xs font-semibold">
            Finished
          </span>
        );
      case "draw":
        return (
          <span className="px-3 py-1 bg-blue-500/20 text-blue-200 rounded-full text-xs font-semibold">
            Draw
          </span>
        );
      default:
        return null;
    }
  };

  const getWinnerBadge = (game: Game) => {
    if (game.status !== "finished") return null;

    const isWinner = game.winner === "X";
    return (
      <span
        className={`px-3 py-1 rounded-full text-xs font-semibold ${
          isWinner
            ? "bg-green-500/20 text-green-200"
            : "bg-red-500/20 text-red-200"
        }`}
      >
        {isWinner ? "Won" : "Lost"}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Dashboard</h1>
            <p className="text-white/70">
              Welcome back, {user?.full_name || user?.email || "Player"}!
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleNewGame}
              className="bg-gradient-to-r from-green-400 to-blue-500 text-white px-6 py-3 rounded-xl hover:from-green-500 hover:to-blue-600 transition-all font-bold shadow-lg transform hover:scale-105"
            >
              🎮 New Game
            </button>
            <button
              onClick={handleLogout}
              className="bg-white/10 backdrop-blur border border-white/30 text-white px-6 py-3 rounded-xl hover:bg-white/20 transition-all font-semibold"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
              <div className="text-white/60 text-sm font-semibold mb-2">Total Games</div>
              <div className="text-3xl font-bold text-white">{stats.total_games}</div>
            </div>
            <div className="bg-green-500/20 backdrop-blur-md border border-green-400/30 rounded-2xl p-6">
              <div className="text-green-200 text-sm font-semibold mb-2">Wins</div>
              <div className="text-3xl font-bold text-white">{stats.wins}</div>
            </div>
            <div className="bg-red-500/20 backdrop-blur-md border border-red-400/30 rounded-2xl p-6">
              <div className="text-red-200 text-sm font-semibold mb-2">Losses</div>
              <div className="text-3xl font-bold text-white">{stats.losses}</div>
            </div>
            <div className="bg-blue-500/20 backdrop-blur-md border border-blue-400/30 rounded-2xl p-6">
              <div className="text-blue-200 text-sm font-semibold mb-2">Win Rate</div>
              <div className="text-3xl font-bold text-white">{stats.win_rate.toFixed(1)}%</div>
            </div>
          </div>
        )}

        {/* Games List */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">Your Games</h2>
            <div className="flex gap-2">
              <button
                onClick={() => setFilter("all")}
                className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                  filter === "all"
                    ? "bg-white/30 text-white"
                    : "bg-white/10 text-white/60 hover:bg-white/20"
                }`}
              >
                All
              </button>
              <button
                onClick={() => setFilter("in_progress")}
                className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                  filter === "in_progress"
                    ? "bg-white/30 text-white"
                    : "bg-white/10 text-white/60 hover:bg-white/20"
                }`}
              >
                Active
              </button>
              <button
                onClick={() => setFilter("finished")}
                className={`px-4 py-2 rounded-lg font-semibold transition-all ${
                  filter === "finished"
                    ? "bg-white/30 text-white"
                    : "bg-white/10 text-white/60 hover:bg-white/20"
                }`}
              >
                Finished
              </button>
            </div>
          </div>

          <div className="space-y-3">
            {games && games.length > 0 ? (
              games.map((game) => (
                <div
                  key={game.id}
                  className="bg-white/10 backdrop-blur border border-white/20 rounded-xl p-4 hover:bg-white/20 transition-all cursor-pointer"
                  onClick={() => game.status === "in_progress" && handleContinueGame(game.id)}
                >
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-4">
                      <div className="text-white/60 text-sm font-mono">#{game.id}</div>
                      {getStatusBadge(game.status)}
                      {getWinnerBadge(game)}
                      <div className="text-white/80 text-sm">
                        Difficulty: <span className="font-semibold">{game.difficulty}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-white/60 text-sm">
                        {new Date(game.updated_at).toLocaleDateString()}
                      </div>
                      {game.status === "in_progress" && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleContinueGame(game.id);
                          }}
                          className="bg-gradient-to-r from-green-400 to-blue-500 text-white px-4 py-2 rounded-lg hover:from-green-500 hover:to-blue-600 transition-all font-semibold text-sm"
                        >
                          Continue
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12 text-white/60">
                No games found. Start a new game!
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

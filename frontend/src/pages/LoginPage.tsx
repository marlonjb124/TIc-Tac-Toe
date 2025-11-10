import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useLogin } from "../hooks/useApi";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();
  const loginMutation = useLogin();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrorMessage("");

    try {
      await loginMutation.mutateAsync({
        username: email,
        password,
      });
      navigate("/dashboard");
    } catch (error: any) {
      const detail = error.response?.data?.detail;
      if (typeof detail === "string") {
        setErrorMessage(detail);
      } else {
        setErrorMessage("Invalid credentials. Please try again.");
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-4">
      <div className="bg-white/10 backdrop-blur-md p-10 rounded-2xl shadow-2xl w-full max-w-md border border-white/20">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Tic-Tac-Toe
          </h1>
          <p className="text-white/70">Sign in to play</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-semibold text-white mb-2"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 bg-white/20 backdrop-blur border border-white/30 rounded-xl text-white placeholder-white/50 focus:ring-2 focus:ring-white/50 focus:outline-none"
              placeholder="admin@tictactoe.com"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-semibold text-white mb-2"
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-3 bg-white/20 backdrop-blur border border-white/30 rounded-xl text-white placeholder-white/50 focus:ring-2 focus:ring-white/50 focus:outline-none"
              placeholder="••••••••"
            />
          </div>

          {errorMessage && (
            <div className="bg-red-500/20 backdrop-blur border border-red-400/30 text-red-100 p-3 rounded-xl text-sm">
              {errorMessage}
            </div>
          )}

          <button
            type="submit"
            disabled={loginMutation.isPending}
            className="w-full bg-gradient-to-r from-green-400 to-blue-500 text-white py-3 px-4 rounded-xl hover:from-green-500 hover:to-blue-600 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all font-bold shadow-lg transform hover:scale-105 disabled:scale-100"
          >
            {loginMutation.isPending ? "Logging in..." : "🎮 Login"}
          </button>
        </form>

        <p className="text-sm text-white/60 text-center mt-6">
          Don't have an account?{" "}
          <Link to="/signup" className="text-white font-semibold hover:underline">
            Sign up here
          </Link>
        </p>

        <p className="text-sm text-white/50 text-center mt-3">
          Default: admin@tictactoe.com / changethis123
        </p>
      </div>
    </div>
  );
}

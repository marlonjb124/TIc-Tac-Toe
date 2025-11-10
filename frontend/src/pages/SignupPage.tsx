import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { authApi } from "../api";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  const signupMutation = useMutation({
    mutationFn: authApi.signup,
    onSuccess: async () => {
      // Auto-login after signup
      const loginResult = await authApi.login({
        username: email,
        password,
      });
      localStorage.setItem("access_token", loginResult.access_token);
      navigate("/dashboard");
    },
    onError: (error: any) => {
      const detail = error.response?.data?.detail;
      if (Array.isArray(detail)) {
        // Validation errors from FastAPI
        const messages = detail.map((err: any) => {
          const field = err.loc?.[err.loc.length - 1] || "field";
          return `${field}: ${err.msg}`;
        });
        setErrorMessage(messages.join(", "));
      } else if (typeof detail === "string") {
        setErrorMessage(detail);
      } else {
        setErrorMessage("Signup failed. Please check your information.");
      }
    },
  });

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrorMessage("");

    if (password !== confirmPassword) {
      setErrorMessage("Passwords don't match");
      return;
    }

    if (password.length < 8) {
      setErrorMessage("Password must be at least 8 characters");
      return;
    }

    try {
      await signupMutation.mutateAsync({
        email,
        password,
        full_name: fullName || undefined,
      });
    } catch (error) {
      // Error already handled by onError
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-4">
      <div className="bg-white/10 backdrop-blur-md p-10 rounded-2xl shadow-2xl w-full max-w-md border border-white/20">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Tic-Tac-Toe
          </h1>
          <p className="text-white/70">Create your account</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-semibold text-white mb-2"
            >
              Email *
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 bg-white/20 backdrop-blur border border-white/30 rounded-xl text-white placeholder-white/50 focus:ring-2 focus:ring-white/50 focus:outline-none"
              placeholder="your@email.com"
            />
          </div>

          <div>
            <label
              htmlFor="fullName"
              className="block text-sm font-semibold text-white mb-2"
            >
              Full Name (optional)
            </label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full px-4 py-3 bg-white/20 backdrop-blur border border-white/30 rounded-xl text-white placeholder-white/50 focus:ring-2 focus:ring-white/50 focus:outline-none"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-semibold text-white mb-2"
            >
              Password *
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="w-full px-4 py-3 bg-white/20 backdrop-blur border border-white/30 rounded-xl text-white placeholder-white/50 focus:ring-2 focus:ring-white/50 focus:outline-none"
              placeholder="••••••••"
            />
          </div>

          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-semibold text-white mb-2"
            >
              Confirm Password *
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={8}
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
            disabled={signupMutation.isPending}
            className="w-full bg-gradient-to-r from-green-400 to-blue-500 text-white py-3 px-4 rounded-xl hover:from-green-500 hover:to-blue-600 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all font-bold shadow-lg transform hover:scale-105 disabled:scale-100"
          >
            {signupMutation.isPending ? "Creating account..." : "🎮 Sign Up"}
          </button>
        </form>

        <p className="text-sm text-white/60 text-center mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-white font-semibold hover:underline">
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface UserStats {
  total_games: number;
  games_in_progress: number;
  games_finished: number;
  wins: number;
  losses: number;
  draws: number;
  win_rate: number;
}

export type GameStatus = "in_progress" | "finished" | "draw";
export type Player = "X" | "O";
export type Difficulty = "EASY" | "MEDIUM" | "HARD";

export interface Game {
  id: number;
  user_id: number;
  board: string[];
  status: GameStatus;
  current_player: Player;
  winner: Player | null;
  difficulty: Difficulty;
  created_at: string;
  updated_at: string;
}

export interface GameCreate {
  difficulty: Difficulty;
}

export interface MoveCreate {
  position: number;
}

export interface MoveResponse {
  position: number;
  player: Player;
  board: string[];
  status: GameStatus;
  winner: Player | null;
  ai_move: number | null;
}

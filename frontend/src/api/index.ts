import { apiClient } from "./client";
import type {
  LoginRequest,
  SignupRequest,
  Token,
  User,
  UserStats,
  Game,
  GameCreate,
  MoveCreate,
  MoveResponse,
} from "../types";

export const authApi = {
  login: async (credentials: LoginRequest): Promise<Token> => {
    const formData = new FormData();
    formData.append("username", credentials.username);
    formData.append("password", credentials.password);

    const { data } = await apiClient.post<Token>("/auth/login/access-token", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    return data;
  },

  signup: async (userData: SignupRequest): Promise<User> => {
    const { data } = await apiClient.post<User>("/auth/signup", userData);
    return data;
  },

  getCurrentUser: async (): Promise<User> => {
    const { data } = await apiClient.get<User>("/users/me");
    return data;
  },

  getUserStats: async (): Promise<UserStats> => {
    const { data } = await apiClient.get<UserStats>("/users/me/stats");
    return data;
  },
};

export const gameApi = {
  createGame: async (gameData: GameCreate): Promise<Game> => {
    const { data } = await apiClient.post<Game>("/games/", gameData);
    return data;
  },

  getGame: async (gameId: number): Promise<Game> => {
    const { data } = await apiClient.get<Game>(`/games/${gameId}`);
    return data;
  },

  makeMove: async (gameId: number, move: MoveCreate): Promise<MoveResponse> => {
    const { data } = await apiClient.post<MoveResponse>(
      `/games/${gameId}/move`,
      move
    );
    return data;
  },

  listGames: async (status?: string): Promise<Game[]> => {
    const params = status ? { status } : {};
    const { data } = await apiClient.get<Game[]>("/games/", { params });
    return data;
  },
};

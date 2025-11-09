import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { authApi, gameApi } from "../api";
import type { LoginRequest, GameCreate, MoveCreate } from "../types";

export const useLogin = () => {
  return useMutation({
    mutationFn: (credentials: LoginRequest) => authApi.login(credentials),
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
    },
  });
};

export const useCurrentUser = () => {
  return useQuery({
    queryKey: ["currentUser"],
    queryFn: () => authApi.getCurrentUser(),
    enabled: !!localStorage.getItem("access_token"),
  });
};

export const useCreateGame = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (gameData: GameCreate) => gameApi.createGame(gameData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["games"] });
    },
  });
};

export const useGame = (gameId: number | null) => {
  return useQuery({
    queryKey: ["game", gameId],
    queryFn: () => gameApi.getGame(gameId!),
    enabled: !!gameId,
  });
};

export const useMakeMove = (gameId: number) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (move: MoveCreate) => gameApi.makeMove(gameId, move),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["game", gameId] });
    },
  });
};

export const useGames = () => {
  return useQuery({
    queryKey: ["games"],
    queryFn: () => gameApi.listGames(),
  });
};

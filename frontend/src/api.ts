import type {
  Move,
  Pokemon,
  Room,
  User,
  BattleState,
} from "./types";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("token");
  const mergedHeaders: Record<string, string> = { "Content-Type": "application/json" };
  if (token) mergedHeaders.Authorization = `Bearer ${token}`;
  if (options.headers) {
    const h = options.headers as Record<string, string>;
    Object.keys(h).forEach((k) => {
      mergedHeaders[k] = h[k];
    });
  }
  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers: mergedHeaders });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Request failed ${res.status}`);
  }
  return res.json();
}

export const api = {
  register: (username: string, password: string) =>
    request<{ user: User; token: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  login: (username: string, password: string) =>
    request<{ user: User; token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  me: () => request<User>("/users/me"),

  searchPokemon: (name: string) =>
    request<Pokemon[]>(`/pokemon/search?name=${encodeURIComponent(name)}`),
  getPokemon: (name: string) => request<Pokemon>(`/pokemon/${name}`),
  getMove: (name: string) => request<Move>(`/moves/${name}`),

  createRoom: () => request<{ room: Room }>("/rooms", { method: "POST" }),
  getRoom: (roomId: string) => request<{ room: Room }>(`/rooms/${roomId}`),
  joinRoom: (roomId: string) =>
    request<{ room: Room }>(`/rooms/${roomId}/join`, { method: "POST" }),
  readyRoom: (roomId: string) =>
    request<{ room: Room }>(`/rooms/${roomId}/ready`, { method: "POST" }),
  leaveRoom: (roomId: string) =>
    request<{ ok: boolean }>(`/rooms/${roomId}/leave`, { method: "DELETE" }),

  createTeam: (pokemonName: string) =>
    request<{ team: Pokemon }>("/teams", {
      method: "POST",
      body: JSON.stringify({ pokemon_name: pokemonName }),
    }),
  getTeams: () => request<{ teams: Pokemon[] }>("/teams"),

  forfeitBattle: (battleId: string) =>
    request<{ ok: boolean }>(`/battles/${battleId}/forfeit`, {
      method: "POST",
    }),
  getBattleHistory: (battleId: string) =>
    request<{ events: BattleState[] }>(`/battles/${battleId}/history`),
};

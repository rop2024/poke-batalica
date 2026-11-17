export type ConnectionStatus = "connected" | "disconnected" | "connecting";

export interface Move {
  name: string;
  power: number | null;
  move_type: string;
  accuracy: number | null;
  pp: number;
}

export interface Pokemon {
  pokemon_id: number;
  name: string;
  types: string[];
  base_hp: number;
  base_attack: number;
  base_defense: number;
  base_special_attack: number;
  base_special_defense: number;
  base_speed: number;
  sprite_url: string | null;
  official_artwork_url: string | null;
  cry_url: string | null;
  moves: Move[];
}

export interface BattlePokemon {
  species: Pokemon;
  current_hp: number;
  max_hp: number;
  fainted: boolean;
}

export interface BattleParticipant {
  player_id: string;
  name: string;
  pokemon: BattlePokemon;
  submitted_move: Move | null;
}

export interface BattleEvent {
  turn: number;
  type: string;
  actor?: string | null;
  target?: string | null;
  move?: string | null;
  damage?: number | null;
  effectiveness?: number | null;
  random_factor?: number | null;
  hp?: number | null;
  max_hp?: number | null;
  winner?: string | null;
  message?: string | null;
}

export interface BattleState {
  battle_id: string;
  turn: number;
  finished: boolean;
  winner: string | null;
  player_a: BattleParticipant;
  player_b: BattleParticipant;
  events: BattleEvent[];
}

export interface Room {
  room_id: string;
  code: string;
  status: "waiting" | "ready" | "battling" | "finished";
  players: Array<{ player_id: string; name: string; ready: boolean }>;
}

export interface User {
  id: string;
  username: string;
  token: string;
}

export interface SoundPrefs {
  master: number;
  music: number;
  effects: number;
  muted: boolean;
}

export interface AppState {
  user: User | null;
  room: Room | null;
  team: Pokemon | null;
  battle: BattleState | null;
  connection: ConnectionStatus;
  sound: SoundPrefs;
}

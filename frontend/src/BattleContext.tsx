import React, { createContext, useContext, useReducer, useCallback, useEffect } from "react";
import io, { type Socket } from "socket.io-client";
import type { AppState, ConnectionStatus, Pokemon, Room, User } from "./types";
import { api } from "./api";
const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || "http://localhost:8000";

export interface AppContextType extends AppState {
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
  createRoom: () => Promise<void>;
  joinRoom: (code: string) => Promise<void>;
  leaveRoom: () => Promise<void>;
  setReady: () => Promise<void>;
  selectPokemon: (pokemon: Pokemon) => void;
  submitMove: (moveName: string) => Promise<void>;
  forfeit: () => Promise<void>;
  toggleSound: () => void;
  setSound: (partial: Partial<AppState["sound"]>) => void;
  connectSocket: (roomId: string) => void;
  disconnectSocket: () => void;
}

const initialSound: AppState["sound"] = {
  master: 0.7,
  music: 0.5,
  effects: 0.8,
  muted: false,
};

const initialState: AppState = {
  user: null,
  room: null,
  team: null,
  battle: null,
  connection: "disconnected",
  sound: initialSound,
};

type Action =
  | { type: "SET_USER"; payload: User }
  | { type: "CLEAR_USER" }
  | { type: "SET_ROOM"; payload: Room }
  | { type: "CLEAR_ROOM" }
  | { type: "SET_TEAM"; payload: Pokemon }
  | { type: "CLEAR_TEAM" }
  | { type: "SET_BATTLE"; payload: AppState["battle"] }
  | { type: "SET_CONNECTION"; payload: ConnectionStatus }
  | { type: "SET_SOUND"; payload: Partial<AppState["sound"]> }
  | { type: "ADD_EVENT"; payload: any };

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case "SET_USER":
      return { ...state, user: action.payload };
    case "CLEAR_USER":
      return { ...state, user: null };
    case "SET_ROOM":
      return { ...state, room: action.payload };
    case "CLEAR_ROOM":
      return { ...state, room: null };
    case "SET_TEAM":
      return { ...state, team: action.payload };
    case "CLEAR_TEAM":
      return { ...state, team: null };
    case "SET_BATTLE":
      return { ...state, battle: action.payload };
    case "SET_CONNECTION":
      return { ...state, connection: action.payload };
    case "SET_SOUND":
      return { ...state, sound: { ...state.sound, ...action.payload } };
    case "ADD_EVENT":
      return {
        ...state,
        battle: state.battle
          ? { ...state.battle, events: [...state.battle.events, action.payload] }
          : null,
      };
    default:
      return state;
  }
}

const AppContext = createContext<AppContextType | null>(null);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const socketRef = React.useRef<Socket | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("user");
    const token = localStorage.getItem("token");
    if (stored && token) {
      try {
        dispatch({ type: "SET_USER", payload: JSON.parse(stored) });
      } catch {
        // ignore
      }
    }
    return () => {
      if (socketRef.current) socketRef.current.disconnect();
    };
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const { user, token } = await api.login(username, password);
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
    dispatch({ type: "SET_USER", payload: user });
  }, []);

  const register = useCallback(async (username: string, password: string) => {
    const { user, token } = await api.register(username, password);
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
    dispatch({ type: "SET_USER", payload: user });
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    if (socketRef.current) socketRef.current.disconnect();
    dispatch({ type: "CLEAR_USER" });
    dispatch({ type: "CLEAR_ROOM" });
    dispatch({ type: "CLEAR_TEAM" });
    dispatch({ type: "SET_BATTLE", payload: null });
    dispatch({ type: "SET_CONNECTION", payload: "disconnected" });
  }, []);

  const createRoom = useCallback(async () => {
    const { room } = await api.createRoom();
    dispatch({ type: "SET_ROOM", payload: room });
  }, []);

  const joinRoom = useCallback(async (code: string) => {
    const rooms = await api.getRoom(code);
    dispatch({ type: "SET_ROOM", payload: rooms.room });
  }, []);

  const leaveRoom = useCallback(async () => {
    if (!state.room) return;
    await api.leaveRoom(state.room.room_id);
    dispatch({ type: "CLEAR_ROOM" });
    dispatch({ type: "CLEAR_TEAM" });
    dispatch({ type: "SET_BATTLE", payload: null });
    if (socketRef.current) socketRef.current.disconnect();
    dispatch({ type: "SET_CONNECTION", payload: "disconnected" });
  }, [state.room]);

  const setReady = useCallback(async () => {
    if (!state.room) return;
    const { room } = await api.readyRoom(state.room.room_id);
    dispatch({ type: "SET_ROOM", payload: room });
  }, [state.room]);

  const selectPokemon = useCallback((pokemon: Pokemon) => {
    dispatch({ type: "SET_TEAM", payload: pokemon });
  }, []);

  const submitMove = useCallback(async (moveName: string) => {
    if (!state.room) return;
    const socket = socketRef.current;
    if (socket) {
      socket.emit("submit_move", { room_id: state.room.room_id, move_name: moveName });
    }
  }, [state.room]);

  const forfeit = useCallback(async () => {
    if (!state.battle) return;
    await api.forfeitBattle(state.battle.battle_id);
  }, [state.battle]);

  const toggleSound = useCallback(() => {
    dispatch({ type: "SET_SOUND", payload: { muted: !state.sound.muted } });
  }, [state.sound.muted]);

  const setSound = useCallback((partial: Partial<AppState["sound"]>) => {
    dispatch({ type: "SET_SOUND", payload: partial });
  }, []);

  const connectSocket = useCallback((roomId: string) => {
    if (socketRef.current) socketRef.current.disconnect();
    const socket = io(SOCKET_URL, { transports: ["websocket"] });
    socketRef.current = socket;

    socket.on("connect", () => dispatch({ type: "SET_CONNECTION", payload: "connected" }));
    socket.on("disconnect", () => dispatch({ type: "SET_CONNECTION", payload: "disconnected" }));
    socket.on("connect_error", () => dispatch({ type: "SET_CONNECTION", payload: "disconnected" }));

    socket.on("player_joined", (data: any) => {
      if (data.room) dispatch({ type: "SET_ROOM", payload: data.room });
    });
    socket.on("player_left", (data: any) => {
      if (data.room) dispatch({ type: "SET_ROOM", payload: data.room });
    });
    socket.on("player_ready", (data: any) => {
      if (data.room) dispatch({ type: "SET_ROOM", payload: data.room });
    });
    socket.on("battle_started", (data: any) => {
      if (data.battle) dispatch({ type: "SET_BATTLE", payload: data.battle });
    });
    socket.on("turn_resolved", (data: any) => {
      if (data.battle) dispatch({ type: "SET_BATTLE", payload: data.battle });
      else if (data.events) {
        data.events.forEach((e: any) => dispatch({ type: "ADD_EVENT", payload: e }));
      }
    });
    socket.on("battle_finished", (data: any) => {
      if (data.battle) dispatch({ type: "SET_BATTLE", payload: data.battle });
    });
    socket.on("error", (data: any) => {
      // surface errors via a toast-like mechanism could go here
      console.error("socket error", data);
    });

    socket.emit("join_room", { room_id: roomId });
  }, []);

  const disconnectSocket = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }
    dispatch({ type: "SET_CONNECTION", payload: "disconnected" });
  }, []);

  const value: AppContextType = {
    ...state,
    login,
    register,
    logout,
    createRoom,
    joinRoom,
    leaveRoom,
    setReady,
    selectPokemon,
    submitMove,
    forfeit,
    toggleSound,
    setSound,
    connectSocket,
    disconnectSocket,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}

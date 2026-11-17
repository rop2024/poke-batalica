import React from "react";
import { useApp } from "../BattleContext";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../api";
import PokemonCard from "../components/PokemonCard";
import PokemonSearch from "../components/PokemonSearch";
import ConnectionStatus from "../components/ConnectionStatus";

export default function LobbyPage() {
  const { user, room, team, createRoom, joinRoom, setReady, selectPokemon, connection } = useApp();
  const navigate = useNavigate();
  const [code, setCode] = React.useState("");
  const [query, setQuery] = React.useState("");
  const [results, setResults] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    if (!query) return;
    setLoading(true);
    api.searchPokemon(query).then(setResults).finally(() => setLoading(false));
  }, [query]);

  const handleCreate = async () => {
    await createRoom();
    navigate(`/room/${room!.room_id}`);
  };

  const handleJoin = async () => {
    await joinRoom(code);
    navigate(`/room/${room!.room_id}`);
  };

  return (
    <div className="col" style={{ gap: 24, maxWidth: 900, margin: "0 auto" }}>
      <ConnectionStatus status={connection} />
      <h1>Lobby</h1>
      <p className="small">Welcome, {user?.username}. Create a room or join one with a friend.</p>

      <div className="row" style={{ gap: 12, flexWrap: "wrap" }}>
        <button className="btn btn-primary" onClick={handleCreate} disabled={loading}>
          {loading ? <span className="spinner" /> : "Create Room"}
        </button>
        <input
          className="search-input"
          type="text"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Room code"
          style={{ width: 150 }}
        />
        <button className="btn btn-ghost" onClick={handleJoin} disabled={loading || !code}>
          Join
        </button>
      </div>

      {room && (
        <div className="card" style={{ marginTop: 16 }}>
          <h2>Room {room.code}</h2>
          <div className="row" style={{ flexWrap: "wrap", gap: 12, alignItems: "flex-start" }}>
            {room.players.map((p) => (
              <div
                key={p.player_id}
                className={`card ${p.ready ? "ready" : ""}`}
                style={{ padding: 12, width: 170, textAlign: "center" }}
              >
                <div className="pokemon-name" style={{ marginBottom: 6 }}>{p.name}</div>
                <div className={`small ${p.ready ? "ready-text" : ""}`}>{p.ready ? "Ready" : "Waiting"}</div>
              </div>
            ))}
          </div>
          {!team && (
            <div style={{ marginTop: 16 }}>
              <h3>Choose your Pokemon</h3>
              <PokemonSearch value={query} onChange={(e) => setQuery(e.target.value)} />
              {loading && <div className="small" style={{ marginTop: 6 }}>Searching...</div>}
              <div style={{ marginTop: 10, display: "flex", flexWrap: "wrap", gap: 10 }}>
                {results.map((p) => (
                  <button
                    key={p.pokemon_id}
                    className="btn btn-ghost"
                    style={{ padding: 8, minWidth: 110 }}
                    onClick={() => selectPokemon(p)}
                  >
                    <img
                      src={p.sprite_url || ""}
                      alt={p.name}
                      className="pokemon-img"
                      style={{ width: 48, height: 48, margin: "0 auto 4px" }}
                      onError={(e) => { (e.target as HTMLImageElement).src = ""; }}
                    />
                    <div className="small">{p.name}</div>
                  </button>
                ))}
              </div>
            </div>
          )}
          {team && (
            <div style={{ marginTop: 16, display: "flex", alignItems: "center", gap: 12 }}>
              <PokemonCard pokemon={team} onSelect={() => {}} />
              <button className="btn btn-primary" onClick={setReady} disabled={room.status !== "waiting"}>
                Mark Ready
              </button>
            </div>
          )}
          <button className="btn btn-danger btn-full" style={{ marginTop: 16 }} onClick={() => { navigate("/lobby"); }}>
            Leave Room
          </button>
        </div>
      )}

      <p className="small" style={{ marginTop: 12, textAlign: "center" }}>
        <Link to="/">Back to home</Link>
      </p>
    </div>
  );
}

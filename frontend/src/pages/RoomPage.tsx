import React from "react";
import { useApp } from "../BattleContext";
import { useNavigate, Link } from "react-router-dom";
import ConnectionStatus from "../components/ConnectionStatus";

export default function RoomPage() {
  const { room, leaveRoom, connection, team, selectPokemon } = useApp();
  const navigate = useNavigate();

  React.useEffect(() => {
    if (room?.status === "battling" && room.players.length === 2) {
      navigate(`/battle/${room.room_id}`);
    }
  }, [room, navigate]);

  if (!room) return <div className="center" style={{ minHeight: "40vh" }}>Loading room...</div>;

  const starterPokemon = [
    { name: "pikachu", types: ["electric"], base_hp: 100, base_attack: 55, base_defense: 40, base_special_attack: 50, base_special_defense: 50, base_speed: 90 },
    { name: "squirtle", types: ["water"], base_hp: 100, base_attack: 48, base_defense: 65, base_special_attack: 50, base_special_defense: 64, base_speed: 43 },
    { name: "bulbasaur", types: ["grass", "poison"], base_hp: 100, base_attack: 49, base_defense: 49, base_special_attack: 65, base_special_defense: 65, base_speed: 45 },
    { name: "charmander", types: ["fire"], base_hp: 100, base_attack: 52, base_defense: 43, base_special_attack: 60, base_special_defense: 50, base_speed: 65 },
    { name: "eevee", types: ["normal"], base_hp: 100, base_attack: 55, base_defense: 50, base_special_attack: 45, base_special_defense: 65, base_speed: 55 },
    { name: "jigglypuff", types: ["normal", "fairy"], base_hp: 100, base_attack: 45, base_defense: 20, base_special_attack: 45, base_special_defense: 25, base_speed: 20 },
  ];

  const moves: any[] = [
    { name: "tackle", power: 40, move_type: "normal", accuracy: 100, pp: 35 },
    { name: "quick-attack", power: 40, move_type: "normal", accuracy: 100, pp: 30 },
    { name: "body-slam", power: 85, move_type: "normal", accuracy: 100, pp: 15 },
    { name: "rest", power: 0, move_type: "psychic", accuracy: null, pp: 10 },
  ];

  return (
    <div className="col" style={{ gap: 20, maxWidth: 700, margin: "0 auto" }}>
      <ConnectionStatus status={connection} />
      <h1>Room {room.code}</h1>
      <div className="card">
        <h2>Players</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {room.players.map((p: { player_id: string; name: string; ready: boolean }) => (
            <div key={p.player_id} className="room-player">
              <span className="room-player-name">{p.name}</span>
              <span className={`room-player-status ${p.ready ? "ready-text" : ""}`}>{p.ready ? "Ready" : "Waiting..."}</span>
            </div>
          ))}
        </div>
      </div>

      {!team && (
        <div className="card">
          <h3 style={{ marginBottom: 10 }}>Choose your Pokemon</h3>
          <div style={{ marginTop: 10, display: "flex", flexWrap: "wrap", gap: 10 }}>
            {starterPokemon.map((p) => (
              <button
                key={p.name}
                className="btn btn-ghost"
                style={{ padding: 10, minWidth: 120 }}
                onClick={() => {
                  selectPokemon({
                    pokemon_id: 0,
                    name: p.name,
                    types: p.types,
                    base_hp: p.base_hp,
                    base_attack: p.base_attack,
                    base_defense: p.base_defense,
                    base_special_attack: p.base_special_attack,
                    base_special_defense: p.base_special_defense,
                    base_speed: p.base_speed,
                    sprite_url: null,
                    official_artwork_url: null,
                    cry_url: null,
                    moves,
                  });
                }}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {team && (
        <div className="card">
          <h3 style={{ marginBottom: 10 }}>Your team</h3>
          <div style={{ marginTop: 10 }}>
            <button className="btn btn-primary" disabled={true}>
              {team.name} selected
            </button>
          </div>
          <button className="btn btn-primary btn-full" style={{ marginTop: 14 }} onClick={() => { }}>
            Mark Ready
          </button>
        </div>
      )}

      <button className="btn btn-danger btn-full" style={{ marginTop: 16 }} onClick={leaveRoom}>
        Leave Room
      </button>
      <p className="small" style={{ marginTop: 12, textAlign: "center" }}>
        <Link to="/lobby">Back to lobby</Link>
      </p>
    </div>
  );
}

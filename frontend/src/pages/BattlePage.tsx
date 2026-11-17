import { useApp } from "../BattleContext";
import { useNavigate } from "react-router-dom";
import BattleArena from "../components/BattleArena";
import HealthBar from "../components/HealthBar";
import MoveButton from "../components/MoveButton";
import BattleLog from "../components/BattleLog";
import ConnectionStatus from "../components/ConnectionStatus";
import SoundToggle from "../components/SoundToggle";

export default function BattlePage() {
  const { battle, user, connection, submitMove, sound } = useApp();
  const navigate = useNavigate();

  const me = battle ? (battle.player_a.player_id === user?.id ? battle.player_a : battle.player_b) : null;
  const opponent = battle && me ? (battle.player_a.player_id === me.player_id ? battle.player_b : battle.player_a) : null;

  if (!battle) return <div className="center" style={{ minHeight: "40vh" }}>Loading battle...</div>;

  return (
    <div className="col" style={{ gap: 14, maxWidth: 900, margin: "0 auto", minHeight: "100vh" }}>
      <div className="row" style={{ justifyContent: "space-between", alignItems: "center", padding: "0 8px" }}>
        <ConnectionStatus status={connection} />
        <SoundToggle sound={sound} onToggle={() => {}} />
      </div>

      <div className="card" style={{ padding: 16 }}>
        <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
          <div className="pokemon-name">{opponent?.name || "Opponent"}</div>
          <div className="small">Turn {battle.turn}</div>
        </div>
        <HealthBar pokemon={opponent!.pokemon} />
        <div style={{ display: "flex", justifyContent: "center", marginTop: 8 }}>
          <img
            src={opponent!.pokemon.species.official_artwork_url || opponent!.pokemon.species.sprite_url || ""}
            alt={opponent!.pokemon.species.name}
            style={{ width: 140, height: 140, opacity: opponent!.pokemon.fainted ? 0.4 : 1, background: "#0f172a", borderRadius: 8 }}
            onError={(e) => { (e.target as HTMLImageElement).src = ""; }}
          />
        </div>
      </div>

      <BattleArena battle={battle} me={me!} opponent={opponent!} />

      <div className="card" style={{ padding: 16 }}>
        <HealthBar pokemon={me!.pokemon} />
        <div style={{ display: "flex", justifyContent: "center", marginTop: 8 }}>
          <img
            src={me!.pokemon.species.official_artwork_url || me!.pokemon.species.sprite_url || ""}
            alt={me!.pokemon.species.name}
            style={{ width: 140, height: 140, opacity: me!.pokemon.fainted ? 0.4 : 1, background: "#0f172a", borderRadius: 8 }}
            onError={(e) => { (e.target as HTMLImageElement).src = ""; }}
          />
        </div>
        <div className="row" style={{ justifyContent: "center", gap: 10, flexWrap: "wrap", marginTop: 14 }}>
          {me!.pokemon.species.moves.map((move) => (
            <MoveButton
              key={move.name}
              move={move}
              disabled={battle.finished || me!.submitted_move !== null || me!.pokemon.fainted}
              onClick={() => submitMove(move.name)}
            />
          ))}
        </div>
        {battle.finished && (
          <button className="btn btn-danger btn-full" style={{ marginTop: 12 }} onClick={() => navigate("/results")}>
            View Results
          </button>
        )}
      </div>

      <BattleLog events={battle.events} />

      {battle.finished && (
        <div className="card" style={{ textAlign: "center", marginTop: 12 }}>
          <h2 className="result-title" style={{ color: battle.winner === user?.id ? "var(--success)" : "var(--danger)", marginBottom: 0 }}>
            {battle.winner === user?.id ? "Victory!" : "Defeat!"}
          </h2>
          <button className="btn btn-primary" onClick={() => navigate("/lobby")} style={{ marginTop: 8 }}>
            Back to Lobby
          </button>
        </div>
      )}
    </div>
  );
}

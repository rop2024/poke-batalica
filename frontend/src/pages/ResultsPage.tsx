import { useApp } from "../BattleContext";
import { useNavigate } from "react-router-dom";

export default function ResultsPage() {
  const { battle, user } = useApp();
  const navigate = useNavigate();

  const me = battle ? (battle.player_a.player_id === user?.id ? battle.player_a : battle.player_b) : null;
  const opponent = battle && me ? (battle.player_a.player_id === me.player_id ? battle.player_b : battle.player_a) : null;
  const won = battle ? battle.winner === user?.id : false;

  return (
    <div className="center" style={{ minHeight: "60vh" }}>
      <div className="card result-card">
        <h1 className="result-title" style={{ color: won ? "var(--success)" : "var(--danger)" }}>
          {won ? "Victory!" : "Defeat!"}
        </h1>
        {me && opponent && (
          <div className="result-row">
            <div className="result-side">
              <div className="result-side-name">{me.name}</div>
              <div className="result-side-poke">{me.pokemon.species.name}</div>
              <div className="result-side-hp">{me.pokemon.current_hp}/{me.pokemon.max_hp} HP</div>
            </div>
            <div className="result-side">
              <div className="result-side-name">{opponent.name}</div>
              <div className="result-side-poke">{opponent.pokemon.species.name}</div>
              <div className="result-side-hp">{opponent.pokemon.current_hp}/{opponent.pokemon.max_hp} HP</div>
            </div>
          </div>
        )}
        {battle && battle.events.length > 0 && (
          <div className="result-events">
            {battle.events.slice(-10).map((e, i) => (
              <div key={i} className="result-event">{e.message}</div>
            ))}
          </div>
        )}
        <div className="row" style={{ justifyContent: "center", gap: 10, marginTop: 12 }}>
          <button className="btn btn-primary" onClick={() => navigate("/lobby")}>
            Rematch / Lobby
          </button>
          <button className="btn btn-ghost" onClick={() => navigate("/")}>
            Home
          </button>
        </div>
      </div>
    </div>
  );
}

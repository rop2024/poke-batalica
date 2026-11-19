import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useApp } from "../BattleContext";
import BattleArena from "../components/BattleArena";
import HealthBar from "../components/HealthBar";
import MoveButton from "../components/MoveButton";
import BattleLog from "../components/BattleLog";
import ConnectionStatus from "../components/ConnectionStatus";
import SoundToggle from "../components/SoundToggle";

export default function BattlePage() {
  const { battle, user, connection, submitMove, sound, playSound, playCry, initAudioCtx } = useApp();
  const navigate = useNavigate();

  const me = battle ? (battle.player_a.player_id === user?.id ? battle.player_a : battle.player_b) : null;
  const opponent = battle && me ? (battle.player_a.player_id === me.player_id ? battle.player_b : battle.player_a) : null;

  const lastEvent = battle?.events[battle.events.length - 1];
  const playedEventsRef = useRef(new Set<number>());

  // Initialize audio context on first render (needs user gesture, handled by SoundToggle)
  useEffect(() => {
    initAudioCtx();
  }, [initAudioCtx]);

  // Play sounds based on battle events
  useEffect(() => {
    if (!lastEvent) return;
    const eventIndex = battle.events.length - 1;
    if (playedEventsRef.current.has(eventIndex)) return;

    switch (lastEvent.type) {
      case "battle_started": {
        playCry(me?.pokemon.species.cry_url ?? null);
        setTimeout(() => playCry(opponent?.pokemon.species.cry_url ?? null), 800);
        break;
      }
      case "attack": {
        playSound("hit");
        if (lastEvent.effectiveness != null) {
          if (lastEvent.effectiveness > 1) {
            playSound("super-effective");
          } else if (lastEvent.effectiveness > 0 && lastEvent.effectiveness < 1) {
            playSound("not-very-effective");
          }
        }
        break;
      }
      case "faint": {
        playSound("faint");
        break;
      }
      case "battle_finished": {
        if (battle.winner === user?.id) {
          playSound("victory");
        } else {
          playSound("defeat");
        }
        break;
      }
      default:
        break;
    }
    playedEventsRef.current.add(eventIndex);
  }, [lastEvent, battle, me, opponent, user, playSound, playCry]);

  // Preload images for both Pokemon
  useEffect(() => {
    const images = [
      me?.pokemon.species.official_artwork_url || me?.pokemon.species.sprite_url,
      opponent?.pokemon.species.official_artwork_url || opponent?.pokemon.species.sprite_url,
    ];
    images.forEach((url) => {
      if (url) {
        const img = new Image();
        img.src = url;
      }
    });
  }, [me, opponent]);

  if (!battle) return <div className="center" style={{ minHeight: "40vh" }}>Loading battle...</div>;

  // Determine the latest attack event to pass effectiveness to HealthBar
  const latestAttack = battle.events.slice().reverse().find((e) => e.type === "attack");
  const oppEffectiveness = latestAttack && latestAttack.target === opponent?.name ? latestAttack.effectiveness : null;
  const meEffectiveness = latestAttack && latestAttack.target === me?.name ? latestAttack.effectiveness : null;

  // Visual state
  const isWaiting = !battle.finished && me?.submitted_move === null && opponent?.submitted_move === null;
  const isAttacking = lastEvent?.type === "attack";
  const isTakingDamageMe = isAttacking && lastEvent?.target === me?.name;
  const isTakingDamageOpp = isAttacking && lastEvent?.target === opponent?.name;

  return (
    <div className="col" style={{ gap: 14, maxWidth: 900, margin: "0 auto", minHeight: "100vh" }}>
      <div className="row" style={{ justifyContent: "space-between", alignItems: "center", padding: "0 8px" }}>
        <ConnectionStatus status={connection} />
        <SoundToggle sound={sound} />
      </div>

      {/* Opponent */}
      <div className="card" style={{ padding: 16, position: "relative" }}>
        <div className="row" style={{ justifyContent: "space-between", alignItems: "center" }}>
          <div className="pokemon-name">{opponent?.name || "Opponent"}</div>
          <div className="small">Turn {battle.turn}</div>
        </div>
        <HealthBar pokemon={opponent!.pokemon} effectiveness={oppEffectiveness} />
        <div style={{ display: "flex", justifyContent: "center", marginTop: 8, position: "relative" }}>
          <img
            src={opponent!.pokemon.species.official_artwork_url || opponent!.pokemon.species.sprite_url || ""}
            alt={opponent!.pokemon.species.name}
            className={`sprite opponent ${opponent!.pokemon.fainted ? "fainted" : ""} ${
              isAttacking && lastEvent?.actor === opponent?.name ? "attacking" : isTakingDamageOpp ? "taking-damage" : ""
            }`}
            style={{ width: 140, height: 140, objectFit: "contain", background: "#0f172a", borderRadius: 8 }}
            onError={(e) => { (e.target as HTMLImageElement).src = ""; }}
          />
        </div>
      </div>

      {/* Battle arena / animation area */}
      <BattleArena battle={battle} me={me!} opponent={opponent!} />

      {/* Player */}
      <div className="card" style={{ padding: 16, position: "relative" }}>
        <HealthBar pokemon={me!.pokemon} effectiveness={meEffectiveness} />
        <div style={{ display: "flex", justifyContent: "center", marginTop: 8, position: "relative" }}>
          <img
            src={me!.pokemon.species.official_artwork_url || me!.pokemon.species.sprite_url || ""}
            alt={me!.pokemon.species.name}
            className={`sprite ${me!.pokemon.fainted ? "fainted" : ""} ${
              isAttacking && lastEvent?.actor === me?.name ? "attacking" : isTakingDamageMe ? "taking-damage" : ""
            }`}
            style={{ width: 140, height: 140, objectFit: "contain", background: "#0f172a", borderRadius: 8 }}
            onError={(e) => { (e.target as HTMLImageElement).src = ""; }}
          />
        </div>
        <div className="row" style={{ justifyContent: "center", gap: 10, flexWrap: "wrap", marginTop: 14 }}>
          {me!.pokemon.species.moves.map((move) => (
            <MoveButton
              key={move.name}
              move={move}
              disabled={battle.finished || me!.submitted_move !== null || me!.pokemon.fainted}
              selected={me!.submitted_move?.name === move.name}
              waiting={isWaiting && !battle.finished}
              onClick={() => {
                playSound("click");
                submitMove(move.name);
              }}
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

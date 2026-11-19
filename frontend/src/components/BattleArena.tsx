import { useEffect, useRef } from "react";
import type { BattleParticipant, BattleState } from "../types";

interface Props {
  battle: BattleState;
  me: BattleParticipant;
  opponent: BattleParticipant;
}

export default function BattleArena({ battle, me, opponent }: Props) {
  const lastEventRef = useRef(battle.events[battle.events.length - 1]?.type ?? null);
  const lastEvent = battle.events[battle.events.length - 1];
  const lastType = lastEvent?.type ?? null;

  // Detect state changes for animation triggers
  useEffect(() => {
    const current = battle.events[battle.events.length - 1]?.type;
    if (current !== lastEventRef.current) {
      lastEventRef.current = current;
    }
  }, [battle.events]);

  // Determine visual state
  const isMyTurn = !battle.finished && me.submitted_move !== null;
  const isWaiting = !battle.finished && me.submitted_move === null && opponent.submitted_move === null;
  const isAttacking = lastType === "attack";
  const isTakingDamage = isAttacking && lastEvent?.target === me.name;
  const state =
    battle.finished
      ? battle.winner === me.player_id ? "victory" : "defeat"
      : isTakingDamage
      ? "taking-damage"
      : isAttacking
      ? "attacking"
      : isMyTurn
      ? "selecting"
      : isWaiting
      ? "waiting"
      : "idle";

  const meImg = me.pokemon.species.official_artwork_url || me.pokemon.species.sprite_url || "";
  const oppImg = opponent.pokemon.species.official_artwork_url || opponent.pokemon.species.sprite_url || "";

  return (
    <div className="card arena">
      <div className="arena-turn">{battle.finished ? "Battle finished" : `Turn ${battle.turn}`}</div>
      <div className="arena-stage">
        {/* Opponent sprite */}
        <div
          className={`sprite opponent ${opponent.pokemon.fainted ? "fainted" : ""} ${state === "attacking" && lastEvent?.actor === opponent.name ? "attacking" : state === "taking-damage" && lastEvent?.target === opponent.name ? "taking-damage" : ""}`}
          style={{ position: "absolute", top: 40, right: 40 }}
        >
          <img
            src={oppImg}
            alt={opponent.pokemon.species.name}
            style={{ width: 120, height: 120, objectFit: "contain", background: "#0f172a", borderRadius: 8 }}
            onError={(e) => { (e.target as HTMLImageElement).src = ""; }}
          />
        </div>

        {/* My sprite */}
        <div
          className={`sprite ${me.pokemon.fainted ? "fainted" : ""} ${state === "attacking" && lastEvent?.actor === me.name ? "attacking" : state === "taking-damage" && lastEvent?.target === me.name ? "taking-damage" : ""}`}
          style={{ position: "absolute", bottom: 40, left: 40 }}
        >
          <img
            src={meImg}
            alt={me.pokemon.species.name}
            style={{ width: 120, height: 120, objectFit: "contain", background: "#0f172a", borderRadius: 8 }}
            onError={(e) => { (e.target as HTMLImageElement).src = ""; }}
          />
        </div>

        {/* State badge */}
        <div className="state-overlay">
          <div className={`state-badge ${state}`}>{state.replace(/-/g, " ")}</div>
        </div>

        {lastEvent && <div className="arena-msg">{lastEvent.message}</div>}
      </div>
      <p className="small" style={{ textAlign: "center" }}>
        {battle.finished ? "The battle has ended." : state === "waiting" ? "Waiting for opponent…" : "Choose your move."}
      </p>
    </div>
  );
}

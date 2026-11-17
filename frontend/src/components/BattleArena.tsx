import type { BattleParticipant, BattleState } from "../types";

interface Props {
  battle: BattleState;
  me: BattleParticipant;
  opponent: BattleParticipant;
}

export default function BattleArena({ battle, me, opponent }: Props) {
  const last = battle.events[battle.events.length - 1];
  return (
    <div className="card arena">
      <div className="arena-turn">{battle.finished ? "Battle finished" : `Turn ${battle.turn}`}</div>
      <div className="arena-stage">
        <div className="arena-label-top">{opponent.name}</div>
        <div className="arena-label-bottom">{me.name}</div>
        {last && <div className="arena-msg">{last.message}</div>}
      </div>
      <p className="small" style={{ textAlign: "center" }}>
        {battle.finished ? "The battle has ended." : "Waiting for moves..."}
      </p>
    </div>
  );
}

import type { BattleEvent } from "../types";

interface Props {
  events: BattleEvent[];
}

export default function BattleLog({ events }: Props) {
  return (
    <div className="card battle-log">
      <div className="battle-log-title">Battle Log</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {events.slice().reverse().map((e, i) => (
          <div key={i} className="battle-log-entry">
            {e.message || `${e.type}`}
          </div>
        ))}
        {events.length === 0 && <div className="small">No events yet.</div>}
      </div>
    </div>
  );
}

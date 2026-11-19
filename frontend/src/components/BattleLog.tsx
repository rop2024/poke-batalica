import { useEffect, useRef } from "react";
import type { BattleEvent } from "../types";

interface Props {
  events: BattleEvent[];
}

export default function BattleLog({ events }: Props) {
  const lastEventRef = useRef(events[events.length - 1]?.type ?? null);

  useEffect(() => {
    const current = events[events.length - 1]?.type;
    lastEventRef.current = current;
  }, [events]);

  const entryColor = (type: string | undefined) => {
    switch (type) {
      case "attack":
        return "var(--accent)";
      case "faint":
        return "var(--danger)";
      case "battle_finished":
        return "var(--success)";
      case "turn_started":
        return "var(--warning)";
      case "turn_resolved":
        return "var(--muted)";
      case "move_submitted":
        return "var(--muted)";
      case "error":
        return "var(--danger)";
      default:
        return "var(--muted)";
    }
  };

  return (
    <div className="card battle-log">
      <div className="battle-log-title">Battle Log</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {events.slice().reverse().map((e, i) => (
          <div
            key={i}
            className={`battle-log-entry ${i === 0 ? "new" : ""}`}
            style={{ color: entryColor(e.type) }}
          >
            {e.message || `${e.type}`}
          </div>
        ))}
        {events.length === 0 && <div className="small">No events yet.</div>}
      </div>
    </div>
  );
}

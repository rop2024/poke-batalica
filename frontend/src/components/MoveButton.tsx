import type { Move } from "../types";

interface Props {
  move: Move;
  disabled: boolean;
  selected: boolean;
  waiting: boolean;
  onClick: () => void;
}

export default function MoveButton({ move, disabled, selected, waiting, onClick }: Props) {
  return (
    <button
      className={`btn btn-ghost move-btn ${selected ? "selected" : ""} ${waiting ? "cooldown" : ""}`}
      disabled={disabled}
      onClick={onClick}
    >
      <div className="move-btn-name">{move.name}</div>
      <div className="move-btn-meta">
        {move.power != null ? `Power ${move.power}` : "Status"} &bull; {move.move_type}
      </div>
      {selected && <div className="small" style={{ color: "var(--accent)", marginTop: 4 }}>Selected</div>}
      {waiting && <div className="small" style={{ color: "var(--warning)", marginTop: 4 }}>Waiting…</div>}
    </button>
  );
}

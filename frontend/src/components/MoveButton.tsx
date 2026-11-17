import type { Move } from "../types";

interface Props {
  move: Move;
  disabled: boolean;
  onClick: () => void;
}

export default function MoveButton({ move, disabled, onClick }: Props) {
  return (
    <button
      className={`btn btn-ghost move-btn ${disabled ? "disabled" : ""}`}
      disabled={disabled}
      onClick={onClick}
    >
      <div className="move-btn-name">{move.name}</div>
      <div className="move-btn-meta">
        {move.power != null ? `Power ${move.power}` : "Status"} &bull; {move.move_type}
      </div>
    </button>
  );
}

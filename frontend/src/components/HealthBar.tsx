import type { BattlePokemon } from "../types";

interface Props {
  pokemon: BattlePokemon;
}

export default function HealthBar({ pokemon }: Props) {
  const pct = Math.max(0, pokemon.current_hp / pokemon.max_hp) * 100;
  const color = pct > 50 ? "var(--success)" : pct > 25 ? "var(--warning)" : "var(--danger)";
  return (
    <div className="health-bar">
      <div className="health-bar-label">
        <span>{pokemon.species.name}</span>
        <span>{pokemon.current_hp} / {pokemon.max_hp}</span>
      </div>
      <div className="health-bar-track">
        <div className="health-bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
      {pokemon.fainted && <div className="health-bar-fainted">{pokemon.species.name} fainted!</div>}
    </div>
  );
}

import type { BattlePokemon } from "../types";

interface Props {
  pokemon: BattlePokemon;
  effectiveness?: number | null;
}

export default function HealthBar({ pokemon, effectiveness }: Props) {
  const pct = Math.max(0, pokemon.current_hp / pokemon.max_hp) * 100;
  const isSuperEffective = effectiveness != null && effectiveness > 1;
  const isNotVeryEffective = effectiveness != null && effectiveness > 0 && effectiveness < 1;

  return (
    <div className="health-bar">
      <div className="health-bar-label">
        <span>{pokemon.species.name}</span>
        <span>{pokemon.current_hp} / {pokemon.max_hp}</span>
      </div>
      <div className="health-bar-track">
        <div
          className={`health-bar-fill ${
            pokemon.current_hp === 0 ? "" : isSuperEffective ? "super-effective" : isNotVeryEffective ? "damage" : ""
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      {pokemon.fainted && <div className="health-bar-fainted">{pokemon.species.name} fainted!</div>}
    </div>
  );
}

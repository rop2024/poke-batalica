import type { Pokemon } from "../types";

interface Props {
  pokemon: Pokemon;
  onSelect: () => void;
}

export default function PokemonCard({ pokemon, onSelect }: Props) {
  return (
    <div className="card pokemon-card" onClick={onSelect}>
      <img
        className="pokemon-img"
        src={pokemon.sprite_url || ""}
        alt={pokemon.name}
        onError={(e) => { (e.target as HTMLImageElement).src = ""; }}
      />
      <div className="pokemon-name">{pokemon.name}</div>
      <div style={{ display: "flex", gap: 4 }}>
        {pokemon.types.map((t) => (
          <span key={t} className="type-chip">{t}</span>
        ))}
      </div>
      <button className="btn btn-ghost" onClick={(e) => { e.stopPropagation(); onSelect(); }}>
        Select
      </button>
    </div>
  );
}

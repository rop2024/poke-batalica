import React from "react";
import type { Pokemon } from "../types";

interface Props {
  pokemon: Pokemon | null;
  onSelect: (p: Pokemon) => void;
}

export default function TeamSelector({ pokemon, onSelect }: Props) {
  const [query, setQuery] = React.useState("");
  const [results, setResults] = React.useState<Pokemon[]>([]);
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    if (!query) return;
    setLoading(true);
    fetch(`http://localhost:8000/pokemon/search?name=${encodeURIComponent(query)}`)
      .then((r) => r.json())
      .then((data: Pokemon[]) => setResults(data))
      .finally(() => setLoading(false));
  }, [query]);

  return (
    <div className="card team-selector">
      <h3 style={{ marginBottom: 10 }}>Select your Pokemon</h3>
      <div style={{ marginBottom: 12 }}>
        <input
          className="search-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search a Pokemon..."
        />
        {loading && <div className="small" style={{ marginTop: 6 }}>Searching...</div>}
      </div>
      <div className="team-grid">
        {results.map((p) => (
          <button
            key={p.pokemon_id}
            className={`btn btn-ghost team-btn ${pokemon?.pokemon_id === p.pokemon_id ? "selected" : ""}`}
            style={{
              border: pokemon?.pokemon_id === p.pokemon_id ? "2px solid var(--accent)" : "1px solid var(--border)",
            }}
            onClick={() => onSelect(p)}
          >
            <img
              className="team-btn-img"
              src={p.sprite_url || ""}
              alt={p.name}
              onError={(e) => { (e.target as HTMLImageElement).src = ""; }}
            />
            <div className="pokemon-name">{p.name}</div>
          </button>
        ))}
        {results.length === 0 && query && <div className="small">No results</div>}
      </div>
      {pokemon && (
        <div className="team-selected">
          <div className="pokemon-name" style={{ marginBottom: 4 }}>Selected: {pokemon.name}</div>
          <button className="btn btn-primary btn-full" onClick={() => onSelect(pokemon)}>
            Confirm
          </button>
        </div>
      )}
    </div>
  );
}

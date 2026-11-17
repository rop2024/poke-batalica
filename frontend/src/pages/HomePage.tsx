import React from "react";
import { useApp } from "../BattleContext";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import PokemonCard from "../components/PokemonCard";
import PokemonSearch from "../components/PokemonSearch";

export default function HomePage() {
  const { user, createRoom, team } = useApp();
  const navigate = useNavigate();
  const [query, setQuery] = React.useState("");
  const [results, setResults] = React.useState<any[]>([]);
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    if (!query) return;
    setLoading(true);
    api.searchPokemon(query).then(setResults).finally(() => setLoading(false));
  }, [query]);

  const handleCreate = async () => {
    await createRoom();
    navigate("/lobby");
  };

  return (
    <div className="center" style={{ minHeight: "60vh" }}>
      <h1 className="result-title">Pokemon Battle</h1>
      <p className="small" style={{ marginBottom: 30 }}>
        Build a team, challenge a friend, and battle in real time.
      </p>

      {!user ? (
        <button className="btn btn-primary btn-full" style={{ maxWidth: 300, marginBottom: 16 }} onClick={() => navigate("/login")}>
          Sign in / Create account
        </button>
      ) : (
        <>
          <div className="col" style={{ maxWidth: 420, width: "100%" }}>
            <label>Search a Pokemon</label>
            <PokemonSearch value={query} onChange={(e) => setQuery(e.target.value)} />
            {loading && <div className="small" style={{ marginTop: 6 }}>Searching...</div>}
            <div style={{ marginTop: 12, maxHeight: 300, overflowY: "auto" }}>
              {results.map((p) => (
                <PokemonCard key={p.pokemon_id} pokemon={p} onSelect={() => {}} />
              ))}
              {results.length === 0 && query && <div className="small">No results</div>}
            </div>
          </div>
          <div className="col" style={{ maxWidth: 420, width: "100%", marginTop: 32 }}>
            <h2>Your Team</h2>
            {team ? (
              <PokemonCard pokemon={team} onSelect={() => {}} />
            ) : (
              <div className="small">No Pokemon selected yet.</div>
            )}
            <button className="btn btn-primary btn-full" style={{ marginTop: 16 }} onClick={handleCreate} disabled={!team}>
              Create Room
            </button>
          </div>
        </>
      )}
    </div>
  );
}

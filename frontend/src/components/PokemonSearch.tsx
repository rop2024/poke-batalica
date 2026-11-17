import React from "react";

interface Props {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export default function PokemonSearch({ value, onChange }: Props) {
  return (
    <div style={{ position: "relative", width: "100%" }}>
      <input
        className="search-input"
        type="text"
        value={value}
        onChange={onChange}
        placeholder="Search a Pokemon..."
      />
    </div>
  );
}

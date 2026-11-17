import requests
from dataclasses import dataclass, field
from typing import List, Optional

POKEAPI_BASE = "https://pokeapi.co/api/v2"


@dataclass
class Move:
    name: str
    power: Optional[int]
    move_type: str
    accuracy: Optional[int]
    pp: int


@dataclass
class PokemonSpecies:
    pokemon_id: int
    name: str
    types: List[str]
    base_hp: int
    base_attack: int
    base_defense: int
    base_special_attack: int
    base_special_defense: int
    base_speed: int
    sprite_url: Optional[str]
    official_artwork_url: Optional[str]
    cry_url: Optional[str]
    moves: List[Move] = field(default_factory=list)


def _get_json(path: str, timeout: int = 10) -> Optional[dict]:
    try:
        response = requests.get(f"{POKEAPI_BASE}{path}", timeout=timeout)
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    return None


def fetch_move(name: str) -> Move:
    data = _get_json(f"/move/{name.lower()}")
    if not data:
        return Move(name=name, power=40, move_type="normal", accuracy=100, pp=30)
    return Move(
        name=data["name"],
        power=data.get("power") or 40,
        move_type=data["type"]["name"],
        accuracy=data.get("accuracy") or 100,
        pp=data.get("pp", 30),
    )


def fetch_pokemon(name: str) -> PokemonSpecies:
    data = _get_json(f"/pokemon/{name.lower()}")
    if not data:
        raise ValueError(f"Could not load Pokemon '{name}' from PokeAPI")

    stats = {s["stat"]["name"]: s["base_stat"] for s in data.get("stats", [])}
    types = [t["type"]["name"] for t in data.get("types", [])]

    moves: List[Move] = []
    for entry in data.get("moves", [])[:4]:
        move_name = entry["move"]["name"]
        moves.append(fetch_move(move_name))

    sprites = data.get("sprites", {}) or {}
    other = sprites.get("other", {}) or {}
    artwork = other.get("official-artwork", {}) or {}
    cries = data.get("cries", {}) or {}

    return PokemonSpecies(
        pokemon_id=data.get("id", 0),
        name=data.get("name", name.lower()),
        types=types or ["normal"],
        base_hp=int(stats.get("hp", 50)),
        base_attack=int(stats.get("attack", 50)),
        base_defense=int(stats.get("defense", 50)),
        base_special_attack=int(stats.get("special-attack", 50)),
        base_special_defense=int(stats.get("special-defense", 50)),
        base_speed=int(stats.get("speed", 50)),
        sprite_url=sprites.get("front_default"),
        official_artwork_url=artwork.get("front_default"),
        cry_url=cries.get("latest"),
        moves=moves,
    )

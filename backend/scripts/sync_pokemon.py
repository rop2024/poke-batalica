"""Synchronize Pokemon and move data from PokeAPI into the local database.

Usage (from the backend directory):

    python scripts/sync_pokemon.py
    python scripts/sync_pokemon.py --pokemon pikachu,squirtle,bulbasaur,charmander,eevee
    python scripts/sync_pokemon.py --limit 151

The script fetches each Pokemon from PokeAPI, extracts the fields the game needs,
and upserts them into the `synced_pokemon` and `synced_moves` tables. It also
fetches each move's power/type/accuracy/pp so battles can resolve damage without
calling PokeAPI at runtime.
"""

import argparse
import json
import os
import sys
import time
from typing import List, Optional

import httpx
from sqlalchemy.orm import Session

# Allow running both as `python scripts/sync_pokemon.py` and as a module.
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.database import SessionLocal, engine  # noqa: E402
from app import models  # noqa: E402

POKEAPI = "https://pokeapi.co/api/v2"
REQUEST_DELAY = 1.0  # seconds between PokeAPI calls (be polite)
MOVE_FETCH_DELAY = 0.3


def fetch_json(client: httpx.Client, path: str, timeout: float = 15.0) -> Optional[dict]:
    try:
        resp = client.get(f"{POKEAPI}{path}", timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def upsert_move(db: Session, move_name: str, client: httpx.Client) -> Optional[dict]:
    """Fetch a single move from PokeAPI and upsert it into synced_moves."""
    data = fetch_json(client, f"/move/{move_name.lower()}")
    if not data:
        return None

    move_type = data.get("type", {}).get("name", "normal")
    move_record = {
        "name": data.get("name", move_name.lower()),
        "power": data.get("power"),
        "move_type": move_type,
        "accuracy": data.get("accuracy"),
        "pp": data.get("pp", 30),
    }

    existing = (
        db.query(models.SyncedMove)
        .filter(models.SyncedMove.name == move_record["name"])
        .first()
    )
    if existing:
        for key, value in move_record.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return {
            "name": existing.name,
            "power": existing.power,
            "move_type": existing.move_type,
            "accuracy": existing.accuracy,
            "pp": existing.pp,
        }

    new_move = models.SyncedMove(**move_record)
    db.add(new_move)
    db.commit()
    db.refresh(new_move)
    return {
        "name": new_move.name,
        "power": new_move.power,
        "move_type": new_move.move_type,
        "accuracy": new_move.accuracy,
        "pp": new_move.pp,
    }


def upsert_pokemon(db: Session, name: str, client: httpx.Client) -> Optional[dict]:
    """Fetch a single Pokemon from PokeAPI and upsert it into synced_pokemon."""
    data = fetch_json(client, f"/pokemon/{name.lower()}")
    if not data:
        print(f"  [skip] {name}: not found on PokeAPI")
        return None

    stats = {s["stat"]["name"]: s["base_stat"] for s in data.get("stats", [])}
    types = [t["type"]["name"] for t in data.get("types", [])]
    sprites = data.get("sprites", {}) or {}
    other = sprites.get("other", {}) or {}
    artwork = other.get("official-artwork", {}) or {}
    cries = data.get("cries", {}) or {}

    # Collect move names (first 4) and sync their move data.
    synced_moves = []
    for entry in data.get("moves", [])[:4]:
        mv_name = entry.get("move", {}).get("name", "")
        if not mv_name:
            continue
        time.sleep(MOVE_FETCH_DELAY)
        move_data = upsert_move(db, mv_name, client)
        if move_data:
            synced_moves.append(move_data)

    pokemon_record = {
        "pokemon_id": data.get("id", 0),
        "name": data.get("name", name.lower()),
        "types": json.dumps(types),
        "base_hp": int(stats.get("hp", 50)),
        "base_attack": int(stats.get("attack", 50)),
        "base_defense": int(stats.get("defense", 50)),
        "base_special_attack": int(stats.get("special-attack", 50)),
        "base_special_defense": int(stats.get("special-defense", 50)),
        "base_speed": int(stats.get("speed", 50)),
        "sprite_url": sprites.get("front_default"),
        "official_artwork_url": artwork.get("front_default"),
        "cry_url": cries.get("latest"),
        "moves": json.dumps(synced_moves),
    }

    existing = (
        db.query(models.SyncedPokemon)
        .filter(models.SyncedPokemon.pokemon_id == pokemon_record["pokemon_id"])
        .first()
    )

    if existing:
        for key, value in pokemon_record.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        result = _pokemon_to_dict(existing, synced_moves)
        print(f"  [updated] {existing.name} (id={existing.pokemon_id}, {len(synced_moves)} moves)")
        return result

    new_pokemon = models.SyncedPokemon(**pokemon_record)
    db.add(new_pokemon)
    db.commit()
    db.refresh(new_pokemon)
    result = _pokemon_to_dict(new_pokemon, synced_moves)
    print(f"  [added] {new_pokemon.name} (id={new_pokemon.pokemon_id}, {len(synced_moves)} moves)")
    return result


def _pokemon_to_dict(pokemon: models.SyncedPokemon, moves: List[dict]) -> dict:
    return {
        "pokemon_id": pokemon.pokemon_id,
        "name": pokemon.name,
        "types": json.loads(pokemon.types) if pokemon.types else [],
        "base_hp": pokemon.base_hp,
        "base_attack": pokemon.base_attack,
        "base_defense": pokemon.base_defense,
        "base_special_attack": pokemon.base_special_attack,
        "base_special_defense": pokemon.base_special_defense,
        "base_speed": pokemon.base_speed,
        "sprite_url": pokemon.sprite_url,
        "official_artwork_url": pokemon.official_artwork_url,
        "cry_url": pokemon.cry_url,
        "moves": moves,
        "synced_at": pokemon.synced_at.isoformat() if pokemon.synced_at else None,
    }


def sync_pokemon_list(names: List[str], limit: Optional[int] = None) -> None:
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    synced_count = 0
    try:
        with httpx.Client(timeout=15.0) as client:
            targets = names[:limit] if limit else names
            for idx, name in enumerate(targets, start=1):
                print(f"[{idx}/{len(targets)}] {name}")
                result = upsert_pokemon(db, name.strip(), client)
                if result:
                    synced_count += 1
                time.sleep(REQUEST_DELAY)
    finally:
        db.close()
    print(f"\nDone. Synced {synced_count} Pokemon.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Pokemon data from PokeAPI")
    parser.add_argument(
        "--pokemon",
        type=str,
        default="pikachu,squirtle,bulbasaur,charmander,eevee,jigglypuff,meowth,psyduck,abra,shellder",
        help="Comma-separated list of Pokemon names to sync",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max number of Pokemon to sync (applied after --pokemon list)",
    )
    args = parser.parse_args()

    names = [n.strip() for n in args.pokemon.split(",") if n.strip()]
    sync_pokemon_list(names, limit=args.limit)


if __name__ == "__main__":
    main()

import httpx
import json
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/pokemon", tags=["pokemon"])
POKEAPI = "https://pokeapi.co/api/v2"

# In-memory cache for frequently used records (avoids repeated PokeAPI/DB hits).
_memory_cache: dict = {}


async def fetch_pokeapi(path: str) -> Optional[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{POKEAPI}{path}")
            if resp.status_code == 200:
                return resp.json()
    except Exception:
        pass
    return None


def parse_pokemon(data: dict) -> schemas.PokemonOut:
    stats = {s["stat"]["name"]: s["base_stat"] for s in data.get("stats", [])}
    types = [t["type"]["name"] for t in data.get("types", [])]
    sprites = data.get("sprites", {}) or {}
    other = sprites.get("other", {}) or {}
    artwork = other.get("official-artwork", {}) or {}
    cries = data.get("cries", {}) or {}
    moves = []
    for entry in data.get("moves", [])[:4]:
        mv = entry.get("move", {})
        moves.append({"name": mv.get("name", ""), "power": None, "move_type": "normal",
                      "accuracy": None, "pp": 30})
    return schemas.PokemonOut(
        pokemon_id=data.get("id", 0),
        name=data.get("name", ""),
        types=types,
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


def models_json_types(value: Optional[str]) -> List[str]:
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        return []


def _synced_pokemon_to_out(pokemon: models.SyncedPokemon) -> schemas.SyncedPokemonOut:
    move_list = models_json_types(pokemon.moves) if pokemon.moves else []
    moves = []
    for mv in move_list:
        moves.append(schemas.SyncedMoveOut(
            name=mv.get("name", ""),
            power=mv.get("power"),
            move_type=mv.get("move_type", "normal"),
            accuracy=mv.get("accuracy"),
            pp=mv.get("pp", 30),
        ))
    return schemas.SyncedPokemonOut(
        pokemon_id=pokemon.pokemon_id,
        name=pokemon.name,
        types=models_json_types(pokemon.types),
        base_hp=pokemon.base_hp,
        base_attack=pokemon.base_attack,
        base_defense=pokemon.base_defense,
        base_special_attack=pokemon.base_special_attack,
        base_special_defense=pokemon.base_special_defense,
        base_speed=pokemon.base_speed,
        sprite_url=pokemon.sprite_url,
        official_artwork_url=pokemon.official_artwork_url,
        cry_url=pokemon.cry_url,
        moves=moves,
        synced_at=pokemon.synced_at,
    )


def _upsert_move_sync(db: Session, move_name: str) -> Optional[models.SyncedMove]:
    existing = (
        db.query(models.SyncedMove)
        .filter(models.SyncedMove.name == move_name.lower())
        .first()
    )
    if existing:
        return existing

    import httpx as _httpx
    try:
        resp = _httpx.get(f"{POKEAPI}/move/{move_name.lower()}", timeout=10.0)
        if resp.status_code != 200:
            return None
        mdata = resp.json()
    except Exception:
        return None

    new_move = models.SyncedMove(
        name=mdata.get("name", move_name.lower()),
        power=mdata.get("power"),
        move_type=mdata.get("type", {}).get("name", "normal"),
        accuracy=mdata.get("accuracy"),
        pp=mdata.get("pp", 30),
    )
    db.add(new_move)
    db.commit()
    db.refresh(new_move)
    return new_move


# ---- Public PokeAPI-proxy endpoints ----

@router.get("/search", response_model=List[schemas.PokemonOut])
async def search_pokemon(name: str):
    data = await fetch_pokeapi(f"/pokemon/{name.lower()}")
    if not data:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    return [parse_pokemon(data)]


# ---- Synced (local cache) endpoints ----
# NOTE: static routes must be registered BEFORE "/{name}" so they are not
# shadowed by the parameterized route.

@router.get("/synced", response_model=List[schemas.SyncedPokemonOut])
def list_synced_pokemon(db: Session = Depends(get_db)):
    """Return all Pokemon that have been synchronized into the local DB."""
    rows = db.query(models.SyncedPokemon).order_by(models.SyncedPokemon.pokemon_id).all()
    return [_synced_pokemon_to_out(r) for r in rows]


@router.get("/synced/{name}", response_model=schemas.SyncedPokemonOut)
def get_synced_pokemon(name: str, db: Session = Depends(get_db)):
    """Return a synced Pokemon by name, falling back to PokeAPI if not cached."""
    row = (
        db.query(models.SyncedPokemon)
        .filter(models.SyncedPokemon.name == name.lower())
        .first()
    )
    if row:
        return _synced_pokemon_to_out(row)

    # Fallback: fetch from PokeAPI, persist, and return.
    try:
        data = asyncio.run(fetch_pokeapi(f"/pokemon/{name.lower()}"))
    except RuntimeError:
        data = None
    if not data:
        raise HTTPException(status_code=404, detail="Pokemon not found")

    stats = {s["stat"]["name"]: s["base_stat"] for s in data.get("stats", [])}
    types = [t["type"]["name"] for t in data.get("types", [])]
    sprites = data.get("sprites", {}) or {}
    other = sprites.get("other", {}) or {}
    artwork = other.get("official-artwork", {}) or {}
    cries = data.get("cries", {}) or {}

    record = {
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
    }
    new_row = models.SyncedPokemon(**record)
    db.add(new_row)
    db.commit()
    db.refresh(new_row)

    # Sync the first 4 moves too.
    move_rows = []
    for entry in data.get("moves", [])[:4]:
        mv_name = entry.get("move", {}).get("name", "")
        if not mv_name:
            continue
        mrow = _upsert_move_sync(db, mv_name)
        if mrow:
            move_rows.append({
                "name": mrow.name,
                "power": mrow.power,
                "move_type": mrow.move_type,
                "accuracy": mrow.accuracy,
                "pp": mrow.pp,
            })
    new_row.moves = json.dumps(move_rows)
    db.commit()

    return _synced_pokemon_to_out(new_row)


@router.get("/{name}", response_model=schemas.PokemonOut)
async def get_pokemon(name: str):
    key = f"pokeapi:pokemon:{name.lower()}"
    if key in _memory_cache:
        return _memory_cache[key]

    data = await fetch_pokeapi(f"/pokemon/{name.lower()}")
    if not data:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    result = parse_pokemon(data)
    _memory_cache[key] = result
    return result


@router.get("/moves/{name}", response_model=schemas.MoveOut)
async def get_move(name: str):
    key = f"pokeapi:move:{name.lower()}"
    if key in _memory_cache:
        return _memory_cache[key]

    data = await fetch_pokeapi(f"/move/{name.lower()}")
    if not data:
        raise HTTPException(status_code=404, detail="Move not found")
    result = schemas.MoveOut(
        name=data.get("name", ""),
        power=data.get("power"),
        move_type=data.get("type", {}).get("name", "normal"),
        accuracy=data.get("accuracy"),
        pp=data.get("pp", 30),
    )
    _memory_cache[key] = result
    return result

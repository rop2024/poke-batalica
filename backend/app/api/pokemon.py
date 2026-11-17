import httpx
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/pokemon", tags=["pokemon"])
POKEAPI = "https://pokeapi.co/api/v2"


async def fetch_pokeapi(path: str):
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f"{POKEAPI}{path}")
        if resp.status_code != 200:
            return None
        return resp.json()


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


@router.get("/search", response_model=List[schemas.PokemonOut])
async def search_pokemon(name: str):
    data = await fetch_pokeapi(f"/pokemon/{name.lower()}")
    if not data:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    return [parse_pokemon(data)]


@router.get("/{name}", response_model=schemas.PokemonOut)
async def get_pokemon(name: str):
    data = await fetch_pokeapi(f"/pokemon/{name.lower()}")
    if not data:
        raise HTTPException(status_code=404, detail="Pokemon not found")
    return parse_pokemon(data)


@router.get("/moves/{name}", response_model=schemas.MoveOut)
async def get_move(name: str):
    data = await fetch_pokeapi(f"/move/{name.lower()}")
    if not data:
        raise HTTPException(status_code=404, detail="Move not found")
    return schemas.MoveOut(
        name=data.get("name", ""),
        power=data.get("power"),
        move_type=data.get("type", {}).get("name", "normal"),
        accuracy=data.get("accuracy"),
        pp=data.get("pp", 30),
    )

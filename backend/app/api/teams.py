import json
from typing import List, Optional
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from .auth import get_current_user

router = APIRouter(prefix="/teams", tags=["teams"])

POKEAPI = "https://pokeapi.co/api/v2"


def _synced_pokemon_data(db: Session, name: str) -> Optional[dict]:
    """Return synced Pokemon data from the local DB if available."""
    row = (
        db.query(models.SyncedPokemon)
        .filter(models.SyncedPokemon.name == name.lower())
        .first()
    )
    if not row:
        return None
    types = json.loads(row.types) if row.types else []
    moves = json.loads(row.moves) if row.moves else []
    return {
        "pokemon_id": row.pokemon_id,
        "name": row.name,
        "types": types,
        "base_hp": row.base_hp,
        "base_attack": row.base_attack,
        "base_defense": row.base_defense,
        "base_special_attack": row.base_special_attack,
        "base_special_defense": row.base_special_defense,
        "base_speed": row.base_speed,
        "sprite_url": row.sprite_url,
        "official_artwork_url": row.official_artwork_url,
        "cry_url": row.cry_url,
        "moves": moves,
    }


def _fetch_pokemon_data(name: str) -> dict:
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(f"{POKEAPI}/pokemon/{name.lower()}")
        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Pokemon '{name}' not found")
        data = resp.json()
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to reach Pokemon data source")

    stats = {s["stat"]["name"]: s["base_stat"] for s in data.get("stats", [])}
    types = [t["type"]["name"] for t in data.get("types", [])]
    sprites = data.get("sprites", {}) or {}
    other = sprites.get("other", {}) or {}
    artwork = other.get("official-artwork", {}) or {}
    cries = data.get("cries", {}) or {}
    moves = []
    for entry in data.get("moves", [])[:4]:
        mv = entry.get("move", {})
        mv_name = mv.get("name", "")
        power = None
        try:
            with httpx.Client(timeout=10.0) as mc:
                mresp = mc.get(f"{POKEAPI}/move/{mv_name}")
            if mresp.status_code == 200:
                power = mresp.json().get("power")
        except Exception:
            pass
        moves.append({
            "name": mv_name,
            "power": power,
            "move_type": "normal",
            "accuracy": None,
            "pp": 30,
        })
    return {
        "pokemon_id": data.get("id", 0),
        "name": data.get("name", ""),
        "types": types,
        "base_hp": int(stats.get("hp", 50)),
        "base_attack": int(stats.get("attack", 50)),
        "base_defense": int(stats.get("defense", 50)),
        "base_special_attack": int(stats.get("special-attack", 50)),
        "base_special_defense": int(stats.get("special-defense", 50)),
        "base_speed": int(stats.get("speed", 50)),
        "sprite_url": sprites.get("front_default"),
        "official_artwork_url": artwork.get("front_default"),
        "cry_url": cries.get("latest"),
        "moves": moves,
    }


def _get_pokemon_data(db: Session, name: str) -> dict:
    """Get Pokemon data, preferring the local synced cache; fall back to PokeAPI."""
    data = _synced_pokemon_data(db, name)
    if data:
        return data
    return _fetch_pokemon_data(name)


@router.post("", response_model=schemas.TeamOut)
def create_team(team_in: schemas.TeamCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    pokemon_data = _get_pokemon_data(db, team_in.pokemon_name)
    team = models.Team(
        pokemon_name=team_in.pokemon_name,
        user_id=current_user.id,
        pokemon_data=json.dumps(pokemon_data),
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.get("", response_model=List[schemas.TeamOut])
def get_teams(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Team).filter(models.Team.user_id == current_user.id).all()

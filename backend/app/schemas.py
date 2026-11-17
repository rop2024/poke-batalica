from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


# ---- Auth ----
class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


# ---- Pokemon ----
class MoveOut(BaseModel):
    name: str
    power: Optional[int] = None
    move_type: str
    accuracy: Optional[int] = None
    pp: int

    class Config:
        from_attributes = True


class PokemonOut(BaseModel):
    pokemon_id: int
    name: str
    types: List[str]
    base_hp: int
    base_attack: int
    base_defense: int
    base_special_attack: int
    base_special_defense: int
    base_speed: int
    sprite_url: Optional[str] = None
    official_artwork_url: Optional[str] = None
    cry_url: Optional[str] = None
    moves: List[MoveOut] = []

    class Config:
        from_attributes = True


# ---- Rooms ----
class RoomOut(BaseModel):
    id: int
    room_id: str
    code: str
    status: str
    players: List[Any] = []

    class Config:
        from_attributes = True


class RoomPlayerOut(BaseModel):
    id: int
    user_id: int
    name: str
    ready: bool

    class Config:
        from_attributes = True


# ---- Teams ----
class TeamCreate(BaseModel):
    pokemon_name: str


class TeamOut(BaseModel):
    id: int
    pokemon_name: str
    pokemon_data: Optional[Any] = None

    class Config:
        from_attributes = True


# ---- Battles ----
class BattleOut(BaseModel):
    id: int
    battle_id: str
    status: str
    winner_user_id: Optional[int] = None

    class Config:
        from_attributes = True


class BattleEventOut(BaseModel):
    id: int
    turn: int
    type: str
    actor: Optional[str] = None
    target: Optional[str] = None
    move: Optional[str] = None
    damage: Optional[int] = None
    effectiveness: Optional[float] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True

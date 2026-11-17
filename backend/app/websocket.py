import json
import asyncio
from typing import Dict, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import models
from .auth import decode_token
from .battles.engine import Battle, BattleParticipant, BattlePokemon, PokemonSpecies, Move

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        # room_id -> {user_id: websocket}
        self.rooms: Dict[str, Dict[int, WebSocket]] = {}

    async def connect(self, room_id: str, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.rooms.setdefault(room_id, {})[user_id] = websocket

    def disconnect(self, room_id: str, user_id: int):
        if room_id in self.rooms:
            self.rooms[room_id].pop(user_id, None)
            if not self.rooms[room_id]:
                del self.rooms[room_id]

    async def send_personal(self, room_id: str, user_id: int, message: dict):
        ws = self.rooms.get(room_id, {}).get(user_id)
        if ws:
            await ws.send_text(json.dumps(message))

    async def broadcast(self, room_id: str, message: dict):
        for user_id, ws in list(self.rooms.get(room_id, {}).items()):
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                self.disconnect(room_id, user_id)

    def get_other_user(self, room_id: str, user_id: int) -> Optional[int]:
        users = list(self.rooms.get(room_id, {}).keys())
        for u in users:
            if u != user_id:
                return u
        return None


manager = ConnectionManager()

# room_id -> Battle engine instance
active_battles: Dict[str, Battle] = {}


def _get_db() -> Session:
    return SessionLocal()


def _verify_token(token: str) -> Optional[int]:
    payload = decode_token(token)
    if not payload:
        return None
    try:
        return int(payload.get("sub"))
    except (TypeError, ValueError):
        return None


def _build_pokemon_species(pokemon_data: dict) -> PokemonSpecies:
    moves = []
    for m in pokemon_data.get("moves", []):
        moves.append(Move(
            name=m.get("name", "tackle"),
            power=m.get("power"),
            move_type=m.get("move_type", "normal"),
            accuracy=m.get("accuracy"),
            pp=m.get("pp", 30),
        ))
    return PokemonSpecies(
        pokemon_id=pokemon_data.get("pokemon_id", 0),
        name=pokemon_data.get("name", "pokemon"),
        types=tuple(pokemon_data.get("types", ["normal"])),
        base_hp=pokemon_data.get("base_hp", 100),
        base_attack=pokemon_data.get("base_attack", 50),
        base_defense=pokemon_data.get("base_defense", 50),
        base_special_attack=pokemon_data.get("base_special_attack", 50),
        base_special_defense=pokemon_data.get("base_special_defense", 50),
        base_speed=pokemon_data.get("base_speed", 50),
        sprite_url=pokemon_data.get("sprite_url"),
        official_artwork_url=pokemon_data.get("official_artwork_url"),
        cry_url=pokemon_data.get("cry_url"),
        moves=moves,
    )


def _init_battle_from_room(room_id: str, db: Session) -> Optional[Battle]:
    room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if not room:
        return None
    players = db.query(models.RoomPlayer).filter(models.RoomPlayer.room_id == room.id).all()
    if len(players) != 2:
        return None
    room.status = "battling"
    db.commit()
    participants = []
    for p in players:
        team = db.query(models.Team).filter(models.Team.user_id == p.user_id).order_by(models.Team.id.desc()).first()
        if not team or not team.pokemon_data:
            return None
        import json as _json
        data = _json.loads(team.pokemon_data)
        species = _build_pokemon_species(data)
        bp = BattlePokemon(species=species, current_hp=species.base_hp, max_hp=species.base_hp)
        participants.append(BattleParticipant(player_id=str(p.user_id), name=p.name, pokemon=bp))
    battle = Battle(battle_id=f"battle-{room_id}", player_a=participants[0], player_b=participants[1])
    # persist battle record
    db_battle = models.Battle(battle_id=battle.battle_id, room_id=room.id, status="active")
    db.add(db_battle)
    db.commit()
    room.status = "battling"
    db.commit()
    return battle


@router.websocket("/ws/rooms/{room_id}")
async def websocket_room(
    websocket: WebSocket,
    room_id: str,
    token: Optional[str] = Query(default=None),
):
    user_id = _verify_token(token) if token else None
    if user_id is None:
        await websocket.close(code=4001)
        return

    db = _get_db()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            await websocket.close(code=4001)
            return
        player = db.query(models.RoomPlayer).join(models.Room).filter(
            models.Room.room_id == room_id,
            models.RoomPlayer.user_id == user_id,
        ).first()
        if not player:
            await websocket.close(code=4003)
            return

        username = user.username
        player_name = player.name

        await manager.connect(room_id, user_id, websocket)
        await manager.broadcast(room_id, {
            "type": "player_joined",
            "room": {"room_id": room_id, "code": room_id, "status": "waiting"},
            "player": {"user_id": user_id, "name": username, "ready": player.ready},
        })

        try:
            while True:
                raw = await websocket.receive_text()
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    await manager.send_personal(room_id, user_id, {"type": "error", "message": "invalid json"})
                    continue

                mtype = msg.get("type")

                if mtype == "submit_move":
                    battle = active_battles.get(room_id)
                    if battle is None:
                        battle = _init_battle_from_room(room_id, db)
                        if battle:
                            active_battles[room_id] = battle
                        else:
                            await manager.send_personal(room_id, user_id, {"type": "error", "message": "battle not ready (both players must pick a Pokemon)"})
                            continue
                    result = battle.submit_move(str(user_id), msg.get("move_name", ""))
                    await manager.send_personal(room_id, user_id, result)
                    await manager.send_personal(room_id, manager.get_other_user(room_id, user_id) or user_id, result)

                    # if both submitted, resolve
                    if battle.player_a.submitted_move and battle.player_b.submitted_move:
                        events = battle.resolve_turn()
                        await manager.broadcast(room_id, {
                            "type": "turn_resolved",
                            "turn": battle.turn,
                            "events": events,
                        })
                        # persist events
                        db_battle = db.query(models.Battle).filter(models.Battle.battle_id == battle.battle_id).first()
                        if db_battle:
                            for ev in events:
                                db.add(models.BattleEvent(
                                    battle_id=db_battle.id, turn=ev.get("turn", 0),
                                    type=ev.get("type", ""), actor=ev.get("actor"),
                                    target=ev.get("target"), move=ev.get("move"),
                                    damage=ev.get("damage"), effectiveness=ev.get("effectiveness"),
                                    message=ev.get("message"),
                                ))
                            db.commit()
                        if battle.finished:
                            db_battle.status = "finished"
                            db.commit()
                            # set winner
                            if battle.winner:
                                win_user = db.query(models.User).filter(models.User.username == battle.winner).first()
                                if win_user:
                                    db_battle.winner_user_id = win_user.id
                                db.commit()

                elif mtype == "ready":
                    player.ready = True
                    db.commit()
                    players = db.query(models.RoomPlayer).filter(models.RoomPlayer.room_id == player.room_id).all()
                    await manager.broadcast(room_id, {
                        "type": "player_ready",
                        "player": {"user_id": user_id, "name": username, "ready": True},
                        "room": {"room_id": room_id, "status": "waiting"},
                    })
                    if len(players) == 2 and all(p.ready for p in players):
                        # init battle
                        if room_id not in active_battles:
                            battle = _init_battle_from_room(room_id, db)
                            if battle:
                                active_battles[room_id] = battle
                                await manager.broadcast(room_id, {
                                    "type": "battle_started",
                                    "battle_id": battle.battle_id,
                                    "turn": 0,
                                    "message": "Battle started!",
                                })

                elif mtype == "ping":
                    await manager.send_personal(room_id, user_id, {"type": "pong"})

                else:
                    await manager.send_personal(room_id, user_id, {"type": "error", "message": f"unknown type {mtype}"})

        except WebSocketDisconnect:
            pass
    finally:
        manager.disconnect(room_id, user_id)
        db.close()
        await manager.broadcast(room_id, {
            "type": "player_left",
            "player": {"user_id": user_id, "name": username},
            "room": {"room_id": room_id},
        })

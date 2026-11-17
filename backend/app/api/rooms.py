import secrets
import string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, auth
from .auth import get_current_user
from ..websocket import active_battles, _init_battle_from_room

router = APIRouter(prefix="/rooms", tags=["rooms"])


def _generate_code(length: int = 6) -> str:
    return "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))


@router.post("", response_model=schemas.RoomOut)
def create_room(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    code = _generate_code()
    while db.query(models.Room).filter(models.Room.code == code).first():
        code = _generate_code()
    room = models.Room(room_id=code, code=code, status="waiting")
    db.add(room)
    db.commit()
    db.refresh(room)
    player = models.RoomPlayer(room_id=room.id, user_id=current_user.id, name=current_user.username, ready=False)
    db.add(player)
    db.commit()
    return _room_out(room, db)


@router.get("/{room_id}", response_model=schemas.RoomOut)
def get_room(room_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return _room_out(room, db)


@router.post("/{room_id}/join", response_model=schemas.RoomOut)
def join_room(room_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if room.status != "waiting":
        raise HTTPException(status_code=400, detail="Room is not open for joining")
    existing = db.query(models.RoomPlayer).filter(
        models.RoomPlayer.room_id == room.id, models.RoomPlayer.user_id == current_user.id
    ).first()
    if existing:
        return _room_out(room, db)
    players = db.query(models.RoomPlayer).filter(models.RoomPlayer.room_id == room.id).all()
    if len(players) >= 2:
        raise HTTPException(status_code=400, detail="Room is full")
    player = models.RoomPlayer(room_id=room.id, user_id=current_user.id, name=current_user.username, ready=False)
    db.add(player)
    db.commit()
    return _room_out(room, db)


@router.post("/{room_id}/ready", response_model=schemas.RoomOut)
def ready_room(room_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    player = db.query(models.RoomPlayer).filter(
        models.RoomPlayer.room_id == room.id, models.RoomPlayer.user_id == current_user.id
    ).first()
    if not player:
        raise HTTPException(status_code=400, detail="Not in room")
    player.ready = True
    db.commit()
    # auto-start when both ready
    players = db.query(models.RoomPlayer).filter(models.RoomPlayer.room_id == room.id).all()
    if len(players) == 2 and all(p.ready for p in players):
        battle = _init_battle_from_room(room_id, db)
        if battle:
            active_battles[room_id] = battle
            room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    return _room_out(room, db)


@router.delete("/{room_id}/leave")
def leave_room(room_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.room_id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    player = db.query(models.RoomPlayer).filter(
        models.RoomPlayer.room_id == room.id, models.RoomPlayer.user_id == current_user.id
    ).first()
    if player:
        db.delete(player)
        db.commit()
    return {"ok": True}


def _room_out(room: models.Room, db: Session) -> dict:
    players = db.query(models.RoomPlayer).filter(models.RoomPlayer.room_id == room.id).all()
    return {
        "id": room.id,
        "room_id": room.room_id,
        "code": room.code,
        "status": room.status,
        "players": [
            {"id": p.id, "user_id": p.user_id, "name": p.name, "ready": p.ready} for p in players
        ],
    }

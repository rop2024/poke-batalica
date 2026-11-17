from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from .auth import get_current_user

router = APIRouter(prefix="/battles", tags=["battles"])


@router.post("/{battle_id}/forfeit")
def forfeit_battle(battle_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    battle = db.query(models.Battle).filter(models.Battle.battle_id == battle_id).first()
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    battle.status = "finished"
    db.commit()
    return {"ok": True}


@router.get("/{battle_id}/history", response_model=List[schemas.BattleEventOut])
def battle_history(battle_id: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    battle = db.query(models.Battle).filter(models.Battle.battle_id == battle_id).first()
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    events = db.query(models.BattleEvent).filter(models.BattleEvent.battle_id == battle.id).order_by(models.BattleEvent.id).all()
    return events

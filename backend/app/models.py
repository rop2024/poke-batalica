from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    rooms = relationship("RoomPlayer", back_populates="user")
    teams = relationship("Team", back_populates="user")
    battles = relationship("Battle", back_populates="creator")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(String(32), unique=True, index=True, nullable=False)
    code = Column(String(8), unique=True, index=True, nullable=False)
    status = Column(String(20), default="waiting")  # waiting, ready, battling, finished
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    players = relationship("RoomPlayer", back_populates="room")
    teams = relationship("Team", back_populates="room")


class RoomPlayer(Base):
    __tablename__ = "room_players"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50), nullable=False)
    ready = Column(Boolean, default=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="players")
    user = relationship("User", back_populates="rooms")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pokemon_name = Column(String(100), nullable=False)
    pokemon_data = Column(Text)  # JSON blob of the Pokemon species
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="teams")
    user = relationship("User", back_populates="teams")


class Battle(Base):
    __tablename__ = "battles"

    id = Column(Integer, primary_key=True, index=True)
    battle_id = Column(String(64), unique=True, index=True, nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    winner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(20), default="active")  # active, finished
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    creator = relationship("User", foreign_keys=[winner_user_id])


class BattleEvent(Base):
    __tablename__ = "battle_events"

    id = Column(Integer, primary_key=True, index=True)
    battle_id = Column(Integer, ForeignKey("battles.id"), nullable=False)
    turn = Column(Integer, default=0)
    type = Column(String(50), nullable=False)
    actor = Column(String(100), nullable=True)
    target = Column(String(100), nullable=True)
    move = Column(String(100), nullable=True)
    damage = Column(Integer, nullable=True)
    effectiveness = Column(Float, nullable=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

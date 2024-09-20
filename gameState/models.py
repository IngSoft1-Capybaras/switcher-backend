from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

# enum de estados de partida
class StateEnum(Enum):
    PLAYING = "playing"
    WAITING = "waiting"
    FINISHED = "finished"

# modelo del estado de la partida
class GameState(Base):
    __tablename__ = 'game_state'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(SQLAEnum(StateEnum), nullable=False)
    idGame = Column(Integer, ForeignKey('games.id'), unique=True, nullable=False)
    currentPlayer = Column(Integer, ForeignKey('players.id'), nullable=True)
    
    game = relationship("Game", back_populates="game_state", uselist=False)
    players = relationship("Player", back_populates="game_state", foreign_keys="[Player.game_state_id]")
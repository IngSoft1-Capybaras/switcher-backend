from enum import Enum
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.db import Base

# Modelo de partida
class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    maxPlayers = Column(Integer, nullable=False)
    minPlayers = Column(Integer, nullable=False)
    
    game_state = relationship("GameState", back_populates="game", uselist=False)
    players = relationship("Player", back_populates="game")
    boxes = relationship("Box", back_populates="game")
    board = relationship("Board", back_populates="game")
    movement_cards = relationship("MovementCard", back_populates="game")
    figure_cards = relationship("FigureCard", back_populates="game")
    
    
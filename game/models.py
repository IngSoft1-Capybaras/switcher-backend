from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database.db import Base

# Modelo de partida
class Game(Base):
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    max_players = Column(Integer, nullable=False)
    min_players = Column(Integer, nullable=False)
    is_private = Column(Boolean, default=False)  # New attribute
    password = Column(String, nullable=True)

    game_state = relationship("GameState", back_populates="game", uselist=False)
    players = relationship("Player", back_populates="game")
    boxes = relationship("Box", back_populates="game")
    board = relationship("Board", back_populates="game")
    movement_cards = relationship("MovementCard", back_populates="game")
    figure_cards = relationship("FigureCard", back_populates="game")

    def players_count(self):
        return len(self.players)
    
    
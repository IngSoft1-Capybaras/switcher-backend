from enum import Enum
from sqlalchemy import Column, Integer, Boolean, Enum as SQLAEnum, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

# Definir un enum de dificultades
class DifficultyEnum(str, Enum):
    EASY = "EASY"
    HARD = "HARD"

# Modelo de carta de figura
class FigureCard(Base):
    __tablename__ = 'figure_cards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    show = Column(Boolean, nullable=False)
    difficulty = Column(SQLAEnum(DifficultyEnum), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=False)

    player = relationship("Player", back_populates="figure_cards")
    game = relationship("Game", back_populates="figure_cards")

from enum import Enum
from sqlalchemy import Column, Integer, Boolean, Enum as SQLAEnum, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

# Definir un enum de dificultades
class DifficultyEnum(str,Enum):
    EASY = "EASY"
    HARD = "HARD"

class typeEnum(str, Enum):
    FIG01 = "FIG01"
    FIG02 = "FIG02"
    FIG03 = "FIG03"
    FIG04 = "FIG04"
    FIG05 = "FIG05"
    FIG06 = "FIG06"
    FIG07 = "FIG07"
    FIG08 = "FIG08"
    FIG09 = "FIG09"
    FIG10 = "FIG10"
    FIG11 = "FIG11"
    FIG12 = "FIG12"
    FIG13 = "FIG13"
    FIG14 = "FIG14"
    FIG15 = "FIG15"
    FIG16 = "FIG16"
    FIG17 = "FIG17"
    FIG18 = "FIG18"
    FIGE01 = "FIGE01"
    FIGE02 = "FIGE02"
    FIGE03 = "FIGE03"
    FIGE04 = "FIGE04"
    FIGE05 = "FIGE05"
    FIGE06 = "FIGE06"
    FIGE07 = "FIGE07"

# Modelo de carta de figura
class FigureCard(Base):
    __tablename__ = 'figure_cards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    show = Column(Boolean, nullable=False)
    difficulty = Column(SQLAEnum(DifficultyEnum), nullable=True)
    player_id = Column(Integer, ForeignKey('players.id', use_alter=True, ondelete='CASCADE'), nullable=False)
    type = Column(SQLAEnum(typeEnum), nullable=False)
    game_id = Column(Integer, ForeignKey('games.id', ondelete='CASCADE'), nullable=False)

    player = relationship("Player", back_populates="figure_cards")
    game = relationship("Game", back_populates="figure_cards")

from enum import Enum
from sqlalchemy import Column, Integer, Boolean, Enum as SQLAEnum, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

# Definir un enum de dificultades
class DifficultyEnum(str,Enum):
    EASY = "EASY"
    HARD = "HARD"

class typeEnum(str,Enum):
    TYPE_1 = "TYPE_1"
    TYPE_2 = "TYPE_2"
    TYPE_3 = "TYPE_3"
    TYPE_4 = "TYPE_4" #H
    TYPE_5 = "TYPE_5" #H
    TYPE_6 = "TYPE_6" #H

# Modelo de carta de figura
class FigureCard(Base):
    __tablename__ = 'figure_cards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    show = Column(Boolean, nullable=False)
    difficulty = Column(SQLAEnum(DifficultyEnum), nullable=True)
    idPlayer = Column(Integer, ForeignKey('players.id', use_alter=True), nullable=False)
    type = Column(SQLAEnum(typeEnum), nullable=False)
    player = relationship("Player", back_populates="figure_cards")

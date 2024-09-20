from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class ColorEnum(Enum):
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"
    YELLOW = "YELLOW"

class Box(Base):
    __tablename__ = 'boxes'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    color = Column(SQLAEnum(ColorEnum), nullable=False)
    posX = Column(Integer, nullable=False)
    posY = Column(Integer, nullable=False)
    idGame = Column(Integer, ForeignKey('games.id'), nullable=False)

    game = relationship("Game", back_populates="boxes")

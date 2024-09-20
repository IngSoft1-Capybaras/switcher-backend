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
    idBoard = Column(Integer, ForeignKey('boards.id'), nullable=False)

    game = relationship("Game", back_populates="boxes")
    board = relationship("Board", back_populates="boxes")  


class Board(Base):
    __tablename__ = 'boards'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_game = Column(Integer, ForeignKey('games.id'), nullable=False)
    
    game = relationship("Game", back_populates="board")
    boxes = relationship("Box", back_populates="board")  

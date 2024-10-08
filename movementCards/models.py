from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.db import Base
from .schemas import typeEnum


# Modelo de MovementCard
class MovementCard(Base):
    __tablename__ = 'movement_cards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    used = Column(Boolean, nullable=False)
    player_id = Column(Integer, ForeignKey('players.id', use_alter=True), nullable=True)
    game_id = Column(Integer, ForeignKey('games.id', use_alter=True))
    type = Column(SQLAEnum(typeEnum), nullable=False)
    
    player = relationship("Player", back_populates="movement_cards")
    game = relationship("Game", back_populates="movement_cards")
    partial_movements = relationship("PartialMovements", back_populates="movement_card")
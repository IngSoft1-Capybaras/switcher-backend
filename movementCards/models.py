from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

# Modelo de MovementCard
class MovementCard(Base):
    __tablename__ = 'movement_cards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    used = Column(Boolean, nullable=False)
    player_id = Column(Integer, ForeignKey('players.id', use_alter=True), nullable=False) # ver bien la necesidad de use_alter
    
    player = relationship("Player", back_populates="movement_cards")

from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict
from .models import typeEnum, DifficultyEnum

# Schema de cartas de figura
class FigureCardSchema(BaseModel):
    id: int
    type: typeEnum
    show: bool
    difficulty: Optional[DifficultyEnum] = None
    player_id: int
    game_id :  int
    
    
    model_config = ConfigDict(from_attributes = True)
    
    
    
from enum import Enum
from pydantic import BaseModel
from .models import typeEnum, DifficultyEnum

# Schema de cartas de figura
class FigureCardSchema(BaseModel):
    type: typeEnum
    show: bool
    difficulty: DifficultyEnum
    player_id: int
    game_id :  int
    
    
    
    
    
    
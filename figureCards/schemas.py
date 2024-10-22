from enum import Enum
from typing import List, Optional, Tuple
from pydantic import BaseModel, ConfigDict
from .models import typeEnum, DifficultyEnum
from board.schemas import BoxIn

# Schema de cartas de figura
class FigureCardSchema(BaseModel):
    id: int
    type: typeEnum
    show: bool
    difficulty: Optional[DifficultyEnum] = None
    player_id: int
    game_id :  int
    
    
    model_config = ConfigDict(from_attributes = True)
    
    
class PlayFigureCardInput(BaseModel):
    player_id: int
    game_id: int
    card_id: int
    figure: List[BoxIn]
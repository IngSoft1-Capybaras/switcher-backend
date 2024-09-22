from enum import Enum
from pydantic import BaseModel
from .models import typeEnum, DifficultyEnum

# Schema de cartas de figura
class FigureCardSchema(BaseModel):
    type: typeEnum
    show: bool
    difficulty: DifficultyEnum
    idPlayer: int
    idGame :  int
    
    
    
    
    
    
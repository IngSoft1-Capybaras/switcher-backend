from enum import Enum
from pydantic import BaseModel

#class Figures(Enum):

# Schema del enum de dificultades
class DifficultyEnum(str, Enum):
    EASY: "EASY"
    HARD: "HARD"

# Schema de cartas de figura
class FigureCardSchema(BaseModel):
    id: int
    show: bool
    difficulty: DifficultyEnum
    player_id: int
    game_id :  int
    
    class Config:
        from_attributes = True
    
    
    
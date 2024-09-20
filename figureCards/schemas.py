from enum import Enum
from pydantic import BaseModel

#class Figures(Enum):

# Schema del enum de dificultades
class DifficultyEnum(Enum):
    EASY: "easy"
    HARD: "hard"

# Schema de cartas de figura
class FigureCardSchema(BaseModel):
    #FALTA TIPO
    show: bool
    difficulty: DifficultyEnum
    player_id: int
    game_id :  int
    
    
    
    
    
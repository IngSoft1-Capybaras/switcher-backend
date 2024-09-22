from enum import Enum
from pydantic import BaseModel

#class Figures(Enum):

# Schema del enum de dificultades
class DifficultyEnum(Enum):
    EASY: "EASY"
    HARD: "HARD"

# Schema de cartas de figura
class FigureCard(BaseModel):
    #FALTA TIPO
    show: bool
    difficulty: DifficultyEnum
    player_id: int
    game_id :  int
    
    
    
    
    
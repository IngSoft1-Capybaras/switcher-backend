from enum import Enum
from pydantic import BaseModel

#class Figures(Enum):

# Schema del enum de dificultades
class DifficultyEnum(Enum):
    EASY: "easy"
    HARD: "hard"

# Schema de cartas de figura
class FigureCard(BaseModel):
    #FALTA TIPO
    show: bool
    difficulty: DifficultyEnum
    idPlayer: int
    idGame :  int
    
    
    
    
    
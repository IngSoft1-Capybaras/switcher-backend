from enum import Enum
from typing import Optional
from pydantic import BaseModel

# Schema del estado de la partida
class StateEnum(str, Enum):
    PLAYING  = "playing"
    WAITING  = "waiting"
    FINISHED = "finished"

# Schema del estado de la partida  
class GameState(BaseModel):
    id           : int
    state        : StateEnum
    idGame       : int
    currentPlayer: int
    #mazo movimiento falta

class GameStateCreate(BaseModel):
    state        : StateEnum
    currentPlayer: Optional[int]
    #mazo movimiento falta
    
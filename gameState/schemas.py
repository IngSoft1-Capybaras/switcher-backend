from enum import Enum
from pydantic import BaseModel

# Schema del estado de la partida
class StateEnum(Enum):
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

    
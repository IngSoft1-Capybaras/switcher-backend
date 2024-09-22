from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from figureCards.schemas import FigureCardSchema
from movementCards.schemas import MovementCard

# schema del enum de turnos
class turnEnum(str,Enum):
    PRIMERO = "PRIMERO"
    SEGUNDO = "SEGUNDO"
    TERCERO = "TERCERO"
    CUARTO  = "CUARTO"


# schema de jugador
class PlayerInDB(BaseModel):
    id: int
    name: str
    turn: Optional[turnEnum] = None
    game_id: int
    game_state_id: int
    host: bool

    class Config:
        from_attributes = True


class PlayerCreateMatch(BaseModel):
    name: str
    host: Optional[bool] = True
    turn: Optional[turnEnum] = None

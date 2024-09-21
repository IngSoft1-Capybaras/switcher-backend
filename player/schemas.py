from enum import Enum
from pydantic import BaseModel
from typing import List, Optional
from figureCards.schemas import FigureCard
from movementCards.schemas import MovementCardSchema

# schema del enum de turnos
class turnEnum(str,Enum):
    PRIMERO = "primero"
    SEGUNDO = "segundo"
    TERCERO = "tercero"
    CUARTO  = "cuarto"


# schema de jugador
class PlayerInDB(BaseModel):
    id: Optional[int]
    name: str
    turn: turnEnum
    game_id: int
    game_state_id: int
    host: bool

    class Config:
        from_attributes = True


class PlayerCreateMatch(BaseModel):
    name: str
    host: Optional[bool] = True
    turn: Optional[turnEnum] = None

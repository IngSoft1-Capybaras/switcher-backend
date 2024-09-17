from enum import Enum
from pydantic import BaseModel
from typing import List
from ..figureCards.schemas import FigureCard
from ..movementCards.schemas import MovementCard

# schema del enum de turnos
class turnEnum(Enum):
    PRIMERO: "primero"
    SEGUNDO: "segundo"
    TERCERO: "tercero"
    CUARTO : "cuarto"


# schema de jugador
class Player(BaseModel):
    id: int
    name: str
    turn: turnEnum
    idGame: int
    idGameStatus: int
    figureCards: List[FigureCard]
    movementCards: List[MovementCard]
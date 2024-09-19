from enum import Enum
from pony.orm import Required, PrimaryKey, Set, Optional
from game.models import Game
from gameState.models import GameState
from figureCards.models import FigureCard
from movementCards.models import MovementCard
from database.db import db

# enum de los turnos
class turnEnum(str,Enum):
    PRIMERO = "primero"
    SEGUNDO = "segundo"
    TERCERO = "tercero"
    CUARTO  = "cuarto"

# modelo de jugador
class Player(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    turn = Optional(turnEnum, nullable=True) 
    host = Required(bool)
    idGame = Required(Game)         
    idGameStatus = Required(GameState)
    figureCards = Set(FigureCard)
    movementCards = Set(MovementCard)

    class Config:
        from_attributes = True
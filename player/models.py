from enum import Enum
from pony.orm import Required, PrimaryKey, Set
from game.models import Game
from gameState.models import GameState
from figureCards.models import FigureCard
from movementCards.models import MovementCard
from database.db import db

# enum de los turnos
class turnEnum(Enum):
    PRIMERO = "primero"
    SEGUNDO = "segundo"
    TERCERO = "tercero"
    CUARTO  = "cuarto"

# modelo de jugador
class Player(db.Entity):
    id = PrimaryKey(int)
    name = Required(str)
    turn = Required(turnEnum)
    idGame = Required(Game)
    idGameStatus = Required(GameState)
    figureCards = Set(FigureCard)
    movementCards = Set(MovementCard)
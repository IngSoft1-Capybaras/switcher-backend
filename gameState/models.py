from enum import Enum
from pony.orm import Required, PrimaryKey, Optional
from database.db import db

# enum de estados de partida
class StateEnum(Enum):
    PLAYING = "playing"
    WAITING = "waiting"
    FINISHED = "finished"

# modelo del estado de la partida
class GameState(db.Entity):
    id =  PrimaryKey(int, auto = True)
    state =  Required(StateEnum)
    idGame =  Required("Game", unique='True')
    currentPlayer =  Optional("Player")
    #mazo movimiento falta
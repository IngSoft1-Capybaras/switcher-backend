from enum import Enum
from pony.orm import Required, PrimaryKey, Set
from ..database.db import db 
from ..gameState.models import GameState
from ..player.models import Player

# Modelo de partida
class Game(db.Entity):
    id =  PrimaryKey(int, auto = True)    
    name =  Required(str)
    maxPlayer =  Required(int) 
    minPlayer =  Required(int)
    gameState =  Required(GameState, unique='True')
    players = Set(Player)
    #private =  Required(bool)
    #password
    
    
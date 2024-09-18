from enum import Enum
from pony.orm import Required, PrimaryKey, Set, Optional
from database.db import db

# Modelo de partida
class Game(db.Entity):
    id =  PrimaryKey(int, auto = True)    
    name =  Required(str)
    maxPlayer =  Required(int) 
    minPlayer =  Required(int)
    gameState =  Optional("GameState")
    players = Set("Player")
    #private =  Required(bool)
    #password
    
    
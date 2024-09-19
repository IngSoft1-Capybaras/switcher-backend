from enum import Enum
from pony.orm import Required, PrimaryKey, Set, Optional
from database.db import db

# Modelo de partida
class Game(db.Entity):
    id =  PrimaryKey(int, auto = True)    
    name =  Required(str)
    maxPlayers =  Required(int) 
    minPlayers =  Required(int)
    gameState =  Optional("GameState")
    players = Set("Player")
    #private =  Required(bool)
    #password
    
    
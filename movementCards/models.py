from enum import Enum
from pony.orm import Required, PrimaryKey
from database.db import db

#class type

class MovementCard(db.Entity):
    #tipo
    id =  PrimaryKey(int, auto = True)
    description =  Required(str)
    used =  Required(bool)
    idPlayer =  Required("Player")
    # ver relacion con GameState
    
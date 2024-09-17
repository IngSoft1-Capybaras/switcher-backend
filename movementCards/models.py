from enum import Enum
from pony.orm import Required, PrimaryKey
from ..database.db import db 
from ..player.models import Player
from ..game.models import Game

#class type

class MovementCard(db.Entity):
    #tipo
    description =  Required(str)
    used =  Required(bool)
    idPlayer =  Required(Player)
    idGame =  Required(Game)
    # ver relacion con GameState
    
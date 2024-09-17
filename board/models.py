from enum import Enum
from pony.orm import Required, PrimaryKey
from ..database.db import db 

class ColorEnum(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"

class Box(db.Entity):
    id =  PrimaryKey(int, auto = True)
    color =  Required(ColorEnum)
    posX = Required(int)
    posY = Required(int)
    idGame = Required(int)
    

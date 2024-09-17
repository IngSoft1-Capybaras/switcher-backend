from enum import Enum
from pony.orm import Required, PrimaryKey
from ..database.db import db 
from ..player.models import Player
from ..game.models import Game

#class Figures(Enum):

# Definir un enum de dificultades
class DifficultyEnum(Enum):
    EASY =  "easy"
    HARD = "hard"

# Modelo de carta de figura
class FigureCard(db.Entity):
    #FALTA TIPO
    id =  PrimaryKey(int, auto = True)
    show =  Required(bool)
    difficulty =  Required(DifficultyEnum)
    idPlayer =  Required(Player)
    idGame =  Required(Game)
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from game.models import Game
from gameState.models import GameState, StateEnum

# Schema del estado de la partida  
class GameStateInDB(BaseModel):
    id           : int
    state        : StateEnum
    game_id       : int
    currentPlayer: Optional[int]
    #mazo movimiento falta

    class Config:
        from_attributes = True

class GameStateCreate(BaseModel):
    state        : StateEnum
    currentPlayer: Optional[int]
    #mazo movimiento falta
    
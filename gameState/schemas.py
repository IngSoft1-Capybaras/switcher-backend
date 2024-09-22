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
    current_player: Optional[int]
    #mazo movimiento falta

    class Config:
        from_attributes = True

class GameStateCreate(BaseModel):
    state        : StateEnum
    current_player: Optional[int]
    #mazo movimiento falta
    
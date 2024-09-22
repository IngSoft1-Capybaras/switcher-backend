from re import I
from pydantic import BaseModel

#class type

class MovementCard(BaseModel):
    #tipo
    description: str
    used: bool
    player_id: int
    game_id: int
    
    
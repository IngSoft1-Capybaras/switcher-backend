from typing import Optional
from pydantic import BaseModel, ConfigDict

# Schema de partida
class GameInDB(BaseModel):
    id: int
    name: str
    max_players: int 
    min_players: int
    # private: bool
    # password: str | None = None
    
    model_config = ConfigDict(from_attributes = True)

class GameCreate(BaseModel):
    name: str
    max_players: int
    min_players: int
    # private: bool
    # password: str | None = None
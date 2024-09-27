from typing import Optional
from pydantic import BaseModel, ConfigDict

# Schema de partida
class GameInDB(BaseModel):
    id: int
    name: str
    maxPlayers: int 
    minPlayers: int
    # private: bool
    # password: str | None = None
    
    model_config = ConfigDict(from_attributes = True)

class GameCreate(BaseModel):
    name: str
    maxPlayers: int
    minPlayers: int
    # private: bool
    # password: str | None = None
from typing import Optional
from pydantic import BaseModel

# Schema de partida
class GameInDB(BaseModel):
    id: int
    name: str
    maxPlayers: int 
    minPlayers: int
    # private: bool
    # password: str | None = None
    
    class Config:
        from_attributes = True

class GameCreate(BaseModel):
    name: str
    maxPlayers: int
    minPlayers: int
    # private: bool
    # password: str | None = None
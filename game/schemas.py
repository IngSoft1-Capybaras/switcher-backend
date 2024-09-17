from typing import Optional
from pydantic import BaseModel

# Schema de partida
class Game(BaseModel):
    id: int
    name: str
    maxPlayer: int 
    minPlayer: int
    private: bool
    password: str | None = None
    
    
    
    
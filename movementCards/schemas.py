from enum import Enum
from pydantic import BaseModel

#class type
class typeEnum(str, Enum):
    LINEAL_CONT = "LINEAL_CONT"
    LINEAL_ESP = "LINEAL_ESP"
    DIAGONAL_CONT = "DIAGONAL_CONT"
    DIAGONAL_ESP = "DIAGONAL_ESP"
    EN_L_DER = "EN_L_DER"
    EN_L_IZQ = "EN_L_IZQ"
    LINEAL_AL_LAT = "LINEAL_AL_LAT"
    
class MovementCardSchema(BaseModel):
    type : typeEnum
    description: str
    used: bool
    player_id: int
    game_id: int

class MovementCardOut(BaseModel):
    type : typeEnum
    description: str
    used: bool
    player_id: int
    
    class Config:
        from_attributes = True
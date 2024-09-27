from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import Optional

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
    id: int
    type : typeEnum
    id: int
    description: str
    used: bool
    player_id: Optional[int]  # Allowing player_id to be None
    game_id: int

    model_config = ConfigDict(from_attributes = True)

class MovementCardOut(BaseModel):
    type : typeEnum
    description: str
    used: bool
    player_id: Optional[int]  # Allowing player_id to be None
    
    model_config = ConfigDict(from_attributes = True)
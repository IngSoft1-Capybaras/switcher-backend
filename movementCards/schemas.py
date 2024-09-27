from enum import Enum
from pydantic import BaseModel
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
    type : typeEnum
    id: int
    description: str
    used: bool
    player_id: Optional[int]  # Allowing player_id to be None
    game_id: int
    
    class Config:
        orm_mode = True  # Needed to work with from_orm
        from_attributes = True

class MovementCardOut(BaseModel):
    type : typeEnum
    description: str
    used: bool
    player_id: Optional[int]  # Allowing player_id to be None
    
    class Config:
        orm_mode = True  # Needed to work with from_orm
        from_attributes = True
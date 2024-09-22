from enum import Enum
from pydantic import BaseModel

class ColorEnum(str, Enum):
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"
    YELLOW = "YELLOW"

    
class Box(BaseModel):
    color: ColorEnum
    posX: int
    posY: int
    id_game: int
    id_board: int

class BoxOut(BaseModel):
    color: ColorEnum
    posX: int
    posY: int
    class ConfigDict:
        from_attributes = True
    
class BoardOut(BaseModel):
    id_game: int
    id: int
    class Config:
        from_attributes = True
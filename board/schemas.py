from typing import List
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
    class Config:
        from_attributes = True
    
class BoardCreate(BaseModel):
    idGame: int
    boxes: List[Box]
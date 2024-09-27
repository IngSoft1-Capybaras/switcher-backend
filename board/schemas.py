from enum import Enum
from pydantic import BaseModel, ConfigDict

class ColorEnum(str, Enum):
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"
    YELLOW = "YELLOW"

    
class Box(BaseModel):
    color: ColorEnum
    pos_x: int
    pos_y: int
    game_id: int
    id_board: int

class BoxOut(BaseModel):
    color: ColorEnum
    pos_x: int
    pos_y: int

    model_config = ConfigDict(from_attributes = True)
    
class BoardOut(BaseModel):
    game_id: int
    id: int

    model_config = ConfigDict(from_attributes = True)

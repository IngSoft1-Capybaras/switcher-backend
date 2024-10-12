from enum import Enum
from pydantic import BaseModel, ConfigDict
from typing import List

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
    highlighted: bool = False

    model_config = ConfigDict(from_attributes = True)

class BoxIn(BaseModel):
    color: ColorEnum
    pos_x: int
    pos_y: int

    model_config = ConfigDict(from_attributes = True)
    
class BoardOut(BaseModel):
    game_id: int
    id: int

    model_config = ConfigDict(from_attributes = True)

class BoardAndBoxesOut(BaseModel):
    game_id: int
    board_id: int
    boxes: List[List[BoxOut]]
    formed_figures: List[List[BoxOut]] = []

    model_config = ConfigDict(from_attributes = True)

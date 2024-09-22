from enum import Enum
from pydantic import BaseModel

class ColorEnum(Enum):
    ROJO: "rojo"
    AMARILLO: "amarillo"
    VERDE: "verde"
    AZUL: "azul"
    
class Box(BaseModel):
    color: ColorEnum
    pos_x: int
    pos_y: int
    game_id: int
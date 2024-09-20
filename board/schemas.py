from ast import List
from enum import Enum
from pydantic import BaseModel

class ColorEnum(Enum):
    ROJO: "ROJO"
    AMARILLO: "AMARILLO"
    VERDE: "VERDE"
    AZUL: "AZUL"
    
class Box(BaseModel):
    color: ColorEnum
    posX: int
    posY: int
    idGame: int
    
class BoardCreate(BaseModel):
    idGame: int
    boxes: List[Box]
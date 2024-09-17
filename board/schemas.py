from enum import Enum
from pydantic import BaseModel

class ColorEnum(Enum):
    ROJO: "rojo"
    AMARILLO: "amarillo"
    VERDE: "verde"
    AZUL: "azul"
    
class Box(BaseModel):
    color: ColorEnum
    posX: int
    posY: int
    idGame: int
import random
from fastapi import Depends
from sqlalchemy.orm import Session
from .models import MovementCard
from .schemas import MovementCardOut, typeEnum
from game.models import Game
from game.game_repository import GameRepository
from .movement_cards_repository import MovementCardsRepository
from database.db import get_db

#VER TEST
class MovementCardUtils:
    
    def __init__(
        self, mov_card_repo: MovementCardsRepository
    ):
        self.mov_card_repo = mov_card_repo
        
    def create_mov_deck(self, game_id: int, db: Session = Depends(get_db),):
        
        #Creamos una lista con los tipos de cartas de movimiento
        types_list = ([typeEnum.DIAGONAL_CONT] * 7 +
                        [typeEnum.DIAGONAL_ESP] * 7  + 
                        [typeEnum.EN_L_DER] * 7 + 
                        [typeEnum.EN_L_IZQ] * 7 + 
                        [typeEnum.LINEAL_AL_LAT] * 7 +
                        [typeEnum.LINEAL_CONT] * 7 +
                        [typeEnum.LINEAL_ESP] * 7
                        )  
        #Random
        random.shuffle(types_list)
        
        #
        for type in types_list:
            self.mov_card_repo.create_movement_card(game_id, type, db)
        
        return {"message": "Movement deck created"}
    
    
    
    
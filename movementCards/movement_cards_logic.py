import random
from fastapi import Depends
from sqlalchemy.orm import Session
from .models import MovementCard
from .schemas import MovementCardOut, typeEnum
from game.models import Game
from game.game_repository import GameRepository
from .movement_cards_repository import MovementCardsRepository
from database.db import get_db
from player.player_repository import PlayerRepository


class MovementCardLogic:
    
    def __init__(
        self, mov_card_repo: MovementCardsRepository, player_repo: PlayerRepository
    ):
        self.mov_card_repo = mov_card_repo
        self.player_repo = player_repo
        
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
        for index,type in enumerate(types_list):
            self.mov_card_repo.create_movement_card(game_id, type, index, db)
        
        # asigno 3 a cada jugador
        players = self.player_repo.get_players_in_game(game_id,db)

        if len(players) == 0:
            return {"message": "Movement deck was not created because there are no players in game"}

        for player in players:
            # obtengo las cartas del juego que quedan en el deck (las que no fueron asignadas a un player aun)
            movDeck = self.mov_card_repo.get_movement_deck(game_id, db)

            # tomo 3 random
            asigned_mov_cards = random.sample(movDeck, 3)

            # las asigno
            for asigned_mov_card in asigned_mov_cards:
                self.mov_card_repo.assign_mov_card(asigned_mov_card.id, player.id, db);


        return {"message": "Movement deck created and assigned to players"}
    
    
def get_mov_cards_logic(mov_card_repo: MovementCardsRepository = Depends(), player_repo: PlayerRepository = Depends()):
    return MovementCardLogic(mov_card_repo, player_repo)
    
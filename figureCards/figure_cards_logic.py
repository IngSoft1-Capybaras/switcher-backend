import random
from sqlalchemy.orm import Session
from .models import FigureCard, typeEnum
from .schemas import FigureCardSchema
from .figure_cards_repository import FigureCardsRepository
from game.models import Game
from player.player_repository import PlayerRepository
from fastapi import Depends

SHOW_LIMIT = 3

class FigureCardsLogic:
    def __init__(
        self, fig_card_repo: FigureCardsRepository, player_repo: PlayerRepository
    ):
        self.fig_card_repo = fig_card_repo
        self.player_repo = player_repo
    
    def create_fig_deck(self, db: Session, game_id: int):

        players = self.player_repo.get_players_in_game(game_id,db)

        if len(players) == 0:
            return {"message": "Figure deck was not created, there no players in game"}
        
        #Creamos una lista con los tipos de cartas de figuras
        
        cards = list(typeEnum)
        
        for player in players:
            #Random
            random.shuffle(cards)

            #armo el mazo para el jugador
            show=True
            for index, figure in enumerate(cards):
                if index == SHOW_LIMIT:
                    show = False
                self.fig_card_repo.create_figure_card(player.id, game_id, figure, show, db)

        return {"message": "Figure deck created"}


def get_fig_cards_logic(fig_card_repo: FigureCardsRepository = Depends(), player_repo: PlayerRepository = Depends()):
    return FigureCardsLogic(fig_card_repo, player_repo)

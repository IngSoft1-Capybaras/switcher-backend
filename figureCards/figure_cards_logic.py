import random
from sqlalchemy.orm import Session
from .models import FigureCard, typeEnum
from .schemas import FigureCardSchema
from .figure_cards_repository import FigureCardsRepository
from game.models import Game
from player.player_repository import PlayerRepository
from fastapi import Depends


AMNT_HARD_CARDS = 10
AMNT_EASY_CARDS = 13
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
        #10 dificiles y 13 fáciles para cada jugador
        hard_cards = (
            [typeEnum.TYPE_4] * 4 + 
            [typeEnum.TYPE_5] * 4 +
            [typeEnum.TYPE_6] * 4
        )
        easy_cards = (
            [typeEnum.TYPE_1] * 5 +
            [typeEnum.TYPE_2] * 5 +
            [typeEnum.TYPE_3] * 5 
        )

        #
        for player in players:
            #Random
            random.shuffle(hard_cards)
            random.shuffle(easy_cards)
            
            #Elijo las cartas para el mazo
            selected_hard_cards = random.sample(hard_cards, AMNT_HARD_CARDS)
            selected_easy_cards = random.sample(easy_cards, AMNT_EASY_CARDS)

            #armo el mazo para el jugador
            combined_deck = selected_hard_cards + selected_easy_cards
            random.shuffle(combined_deck)
            show=True
            for index, figure in enumerate(combined_deck):
                if index == SHOW_LIMIT:
                    show = False
                self.fig_card_repo.create_figure_card(player.id, game_id, figure, show, db)

        return {"message": "Figure deck created"}


def get_fig_cards_logic(fig_card_repo: FigureCardsRepository = Depends(), player_repo: PlayerRepository = Depends()):
    return FigureCardsLogic(fig_card_repo, player_repo)

import random
from sqlalchemy.orm import Session
from .models import FigureCard, typeEnum
from .schemas import FigureCardSchema
from .figure_card_repository import FigureCardRepository
from game.models import Game
from player.player_repository import PlayerRepository



class FigureCardUtils:
    def __init__(
        self, fig_card_repo: FigureCardRepository, player_repo: PlayerRepository
    ):
        self.fig_card_repo = fig_card_repo
        self.player_repo = player_repo
    
    def create_fig_deck(self, db: Session, game_id: int):

        players = self.player_repo.get_players_in_game(game_id)
        #PREGUNTAR DUDA ARMAR MAZO FIGURAS
        #Creamos una lista con los tipos de cartas de figuras
        fig_list = (
                        [typeEnum.TYPE_4] * 3 + 
                        [typeEnum.TYPE_5] * 4 +
                        [typeEnum.TYPE_6] * 3 +
                        [typeEnum.TYPE_1] * 5 +
                        [typeEnum.TYPE_2] * 4 +
                        [typeEnum.TYPE_3] * 4 
                    )  

        #
        for player in players:
            #Random
            random.shuffle(fig_list)

            for figure in fig_list:
                self.fig_card_repo.create_figure_card(player.id, game_id, figure)

        return {"message": "Figure deck created"}
    
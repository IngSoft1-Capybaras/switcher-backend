import random
from sqlalchemy.orm import Session
from .models import FigureCard, typeEnum, DirectionEnum, FigurePaths
from .schemas import FigureCardSchema
from .figure_cards_repository import FigureCardsRepository
from game.models import Game
from player.player_repository import PlayerRepository
from board.board_repository import BoardRepository
from board.board_logic import BoardLogic
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

    def get_pointer_from_figure(self,figure):
        if len(figure) == 0:
            raise HTTPException(status_code=404, detail="Empty figure")
        
        x = figure[0].pos_x
        y = figure[0].pos_y
        # obtener la casilla con el x menor y el y mayor
        for box in figure:
            if box.pos_x < x:
                x = box.pos_x
            if box.pos_y > y:
                y = box.pos_y

        return (x,y)

    def check_valid_figure(self,figure,figure_type,board, db):
        pointer = self.get_pointer_from_figure(figure)
        boardLogic = BoardLogic(BoardRepository())
        color = BoardLogic.get_box_color(boardLogic, board.board_id, pointer[0], pointer[1], db)
        for path in FigurePaths:
            if path.type == figure_type:
                # return check_path(path.path, figure, pointer, board, color)
                return True

        # for box in figure:
        #     pointer = move_pointer(pointer, box.direction)
        #     if not board.is_box_in(pointer):
        #         return False

        return True

    def play_figure_card(self, figureInfo, db):
        print([repr(path) for path in FigurePaths])
        player = self.player_repo.get_player_by_id(figureInfo.game_id, figureInfo.player_id, db)
        board_repo = BoardRepository()
        board = BoardRepository.get_configured_board(board_repo, figureInfo.game_id, db)
        figure_card = self.fig_card_repo.get_figure_card_by_id(figureInfo.game_id, figureInfo.player_id, figureInfo.card_id, db)
        if not figure_card.show:
            return {"message": "The card is not shown"}
        # chequear que la figura es valida (compara con la figura de la carta)
        valid = self.check_valid_figure( figureInfo.figure, figure_card.type, board, db)

        if valid:
            # figure_card.show = False
            # figure_card.player_id = None
            return {"message": "Figure card played"}
        else:
            return {"message": "Invalid figure"}


def get_fig_cards_logic(fig_card_repo: FigureCardsRepository = Depends(), player_repo: PlayerRepository = Depends()):
    return FigureCardsLogic(fig_card_repo, player_repo)

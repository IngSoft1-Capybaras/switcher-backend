import random
from sqlalchemy.orm import Session
from .models import FigureCard, typeEnum, DirectionEnum, FigurePaths, direction_map
from .schemas import FigureCardSchema
from .figure_cards_repository import FigureCardsRepository
from game.models import Game
from player.player_repository import PlayerRepository
from board.board_repository import BoardRepository
from gameState.game_state_repository import GameStateRepository
from board.board_logic import BoardLogic
from fastapi import Depends
from fastapi import HTTPException
from connection_manager import manager

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

    def is_valid_pointer(self, pointer):
        return pointer[0] >= 0 and pointer[0] <= 5 and pointer[1] >= 0 and pointer[1] <= 5

    def check_surroundings(self, path, figure, pointer, board, color, db):
        print(f"\n(47) Checking surroundings for pointer: {pointer}\n")
        boardLogic = BoardLogic(BoardRepository())
        # chequear que las casillas de alrededor del pointer dado sean de distinto color
        for direction in DirectionEnum:
            # chequear que la casilla de alrededor de la figura sea del color de la figura
            pointerBefore = pointer
            pointer = self.move_pointer(pointer, direction)
            if self.is_valid_pointer(pointer):
                if (boardLogic.get_box_color(board.board_id, pointer[0], pointer[1], db) == color) and not self.belongs_to_figure(pointer, figure):
                    return False
                else: # retrotraer el pointer
                    pointer = pointerBefore
                
        return True


    def move_pointer(self, pointer, direction):
        if direction == DirectionEnum.UP:
            pointer = (pointer[0], pointer[1] - 1)
        elif direction == DirectionEnum.DOWN:
            pointer = (pointer[0], pointer[1] + 1)
        elif direction == DirectionEnum.LEFT:
            pointer = (pointer[0] - 1, pointer[1])
        elif direction == DirectionEnum.RIGHT:
            pointer = (pointer[0] + 1, pointer[1])
        return pointer

    def belongs_to_figure(self, pointer, figure):
        for fig_box in figure:
            if fig_box.pos_x == pointer[0] and fig_box.pos_y == pointer[1]:
                return True
        return False

    def check_path(self, path, figure, pointer, board, color, db):
        boardLogic = BoardLogic(BoardRepository())
        result = True
        for i, box in enumerate(figure):
            # if not BoardLogic.is_box_in(pointer):
            #     result = False
            check_surroundings = self.check_surroundings(path, figure, pointer, board, color, db)
            # check if the current pointer points to a box from our figure
            inBounds = self.belongs_to_figure(pointer, figure)
            # if not inBounds:
                # raise HTTPException(status_code=404, detail="Boxes given out of type figure bounds")
                # result = {'message': "Boxes given out of type figure bounds"}
            result = result and (boardLogic.get_box_color(board.board_id , pointer[0] , pointer[1], db) == color) and inBounds and check_surroundings
            print(f"\n(72) Result: {result}\n")
            print(f"\n(73) PointerBefore: {pointer}\n")
            if not result:
                break
            # si no es la ultima casilla de la figura, mover el pointer 
            # bug: si la figura es de mas longitud que el path - 1 
            # (esto no deberia pasar de todas maneras a no ser que se pase una figura de tipo X y longitud X con longitud Y != X)
            if i < len(path):
                print(f"\n(77) Path: {path[i]}\n")
                pointer = self.move_pointer(pointer, path[i])
                # Antes de seguir fijarse de que no se salga de los limites del tablero
                if not self.is_valid_pointer(pointer):
                    result = False
                    break
                print(f"\n(79) PointerAfter: {pointer}\n")

        return result

    def get_pointer_from_figure(self,figure, rot):
        if len(figure) == 0:
            raise HTTPException(status_code=404, detail="Empty figure")

        # PRINT line of code also
        print(f"\n(88) rot: {rot}\n")
        
        x = figure[0].pos_x
        y = figure[0].pos_y
        # dependiendo de la rotacion aplicada actualmente, el punto de referencia de la figura
        # (0 grados = punta arriba izquierda) (90g = punta arriba derecha) (180 = punta abajo derecha) (270 = punta abajo izquierda)
        # los elementos 0,0 estan en la punta izquierda mas alta

        if rot == 0:
            # Encuentra el valor mínimo de x
            min_x = min(box.pos_x for box in figure)

            # Filtra las cajas que tienen el valor mínimo de x
            min_x_boxes = [box for box in figure if box.pos_x == min_x]

            # Encuentra el valor mínimo de y entre las cajas con el valor mínimo de x
            min_y = min(box.pos_y for box in min_x_boxes)

            # Ahora min_x es el valor mínimo de x y min_y es el valor mínimo de y entre las cajas con el valor mínimo de x
            x = min_x
            y = min_y
        elif rot == 1:
            # Encuentra el valor máximo de y
            max_y = max(box.pos_y for box in figure)

            # Filtra las cajas que tienen el valor máximo de y
            max_y_boxes = [box for box in figure if box.pos_y == max_y]

            # Encuentra el valor mínimo de x entre las cajas con el valor máximo de y
            min_x = min(box.pos_x for box in max_y_boxes)

            # Ahora min_x es el valor mínimo de x y max_y es el valor máximo de y entre las cajas con el valor máximo de y
            x = min_x
            y = max_y
        elif rot == 2:
            # Encuentra el valor máximo de x
            max_x = max(box.pos_x for box in figure)

            # Filtra las cajas que tienen el valor máximo de x
            max_x_boxes = [box for box in figure if box.pos_x == max_x]

            # Encuentra el valor máximo de y entre las cajas con el valor máximo de x
            max_y = max(box.pos_y for box in max_x_boxes)

            # Ahora max_x es el valor máximo de x y max_y es el valor máximo de y entre las cajas con el valor máximo de x
            x = max_x
            y = max_y
        elif rot == 3:
            # Encuentra el valor mínimo de y
            min_y = min(box.pos_y for box in figure)

            # Filtra las cajas que tienen el valor mínimo de y
            min_y_boxes = [box for box in figure if box.pos_y == min_y]

            # Encuentra el valor máximo de x entre las cajas con el valor mínimo de y
            max_x = max(box.pos_x for box in min_y_boxes)

            # Ahora max_x es el valor máximo de x y min_y es el valor mínimo de y entre las cajas con el valor mínimo de y
            x = max_x
            y = min_y
        else:
            raise HTTPException(status_code=404, detail="Invalid rotation")
            

        return (x,y)


    def check_valid_figure(self,figure,figure_type,board, db):
        pointer = self.get_pointer_from_figure(figure,0)
        boardLogic = BoardLogic(BoardRepository())
        color = BoardLogic.get_box_color(boardLogic, board.board_id, pointer[0], pointer[1], db)
        if color != figure[0].color:
            raise HTTPException(status_code=404, detail="Color of figure does not match with color in board")
        validType = False
        result = False
        for path in FigurePaths:
            if path.type == figure_type:
                # chequear las 4 rotaciones posibles del path
                for i in range(4):
                    # Chequear los 4 posibles puntos de referencia de la figura (depende de que tan rotada venga) 
                    for j in range(4):

                        # Cambiar el pointer a la posición inicial de la figura rotada 90 grados j veces
                        pointer = self.get_pointer_from_figure(figure, j)

                        partial_result = self.check_path(path.path, figure, pointer, board, color, db)
                        # Si una de las rotaciones sigue un path valido, la figura es valida (luego chequearemos que no se superpongan)
                        if partial_result:
                            result = True
                            break

                    # Rota el path 90 grados
                    path.path = [direction_map[direction] for direction in path.path]
                    if partial_result:
                        break

                validType = True
                break
        if partial_result == {'message': "Boxes given out of type figure bounds"}:
            raise HTTPException(status_code=404, detail="Boxes given out of type figure bounds")
        return result

        if not validType:
            raise HTTPException(status_code=404, detail="Invalid figure type")

        return result

    def modifiyBoardTest(self, board, db):
        boardLogic = BoardLogic(BoardRepository())
        boardRepo = BoardRepository()
        board = boardRepo.get_configured_board(board.game_id, db)
        # Modificar las casillas para formar una figura valida
        boardRepo.upd_box_color(board.board_id, 2, 2, "RED", db)
        boardRepo.upd_box_color(board.board_id, 2, 3, "RED", db)
        boardRepo.upd_box_color(board.board_id, 1, 3, "RED", db)
        boardRepo.upd_box_color(board.board_id, 1, 4, "RED", db)
        boardRepo.upd_box_color(board.board_id, 1, 5, "RED", db)

        # agrego una a los surroundings para prover nueva funcion
        boardRepo.upd_box_color(board.board_id, 1, 2, "RED", db)

        return board

    async def play_figure_card(self, figureInfo, db):
        print([repr(path) for path in FigurePaths])

        gameStateRepo = GameStateRepository()
        board_repo = BoardRepository()

        player = self.player_repo.get_player_by_id(figureInfo.game_id, figureInfo.player_id, db)
        gameState = gameStateRepo.get_game_state_by_id(figureInfo.game_id, db)

        # chequear que sea el turno del jugador
        if player.id != gameState.current_player:
            return {"message": "It is not the player's turn"}

        board = BoardRepository.get_configured_board(board_repo, figureInfo.game_id, db)
        figure_card = self.fig_card_repo.get_figure_card_by_id(figureInfo.game_id, figureInfo.player_id, figureInfo.card_id, db)

        # chequear que la carta de figura sea del jugador
        if figure_card.player_id != player.id:
            return {"message": "The figure card does not belong to the player"}
        if not figure_card.show:
            return {"message": "The card is not shown"}

        # lets modify the existing board to have a figure to test this validation
        # board = self.modifiyBoardTest(board, db)
        
        # chequear que la figura es valida (compara con la figura de la carta)
        valid = self.check_valid_figure( figureInfo.figure, figure_card.type, board, db)

        if valid:
            # Eliminar carta de figura
            self.fig_card_repo.delete_figure_card(figureInfo.player_id, figureInfo.game_id, figureInfo.card_id, db)

            # TODO : Pasar movimientos de movimiento parcial a movimiento completo

            # Avisar por websocket que se jugo una carta de figura
            game_id = figureInfo.game_id
            message = {
                    "type":f"{game_id}:FIGURE_UPDATE"
                }
            await manager.broadcast(message)

            return {"message": "Figure card played"}
        else:
            return {"message": "Invalid figure"}


def get_fig_cards_logic(fig_card_repo: FigureCardsRepository = Depends(), player_repo: PlayerRepository = Depends()):
    return FigureCardsLogic(fig_card_repo, player_repo)

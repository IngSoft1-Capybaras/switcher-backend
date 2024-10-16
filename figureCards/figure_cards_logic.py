import logging
import random

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from board.board_repository import BoardRepository
from connection_manager import manager
from game.models import Game
from gameState.game_state_repository import GameStateRepository
from player.player_repository import PlayerRepository
from board.board_repository import BoardRepository
from gameState.game_state_repository import GameStateRepository

from .figure_cards_repository import FigureCardsRepository
from .models import (DirectionEnum, FigureCard, FigurePaths, direction_map,
                     typeEnum)
from .schemas import FigureCardSchema
from fastapi import HTTPException
from connection_manager import manager

SHOW_LIMIT = 3
logging.basicConfig(filename='output.log', level=logging.DEBUG)

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

    def check_surroundings(self, path, figure, pointer, board_id, color, db):
        print(f"\n(62) Checking surroundings for pointer: {pointer}\n")
        board_repo = BoardRepository()
        # chequear que las casillas de alrededor del pointer dado sean de distinto color
        for direction in DirectionEnum:
            print(f"\n(66) Check surr Direction: {direction}\n")
            # chequear que la casilla de alrededor de la figura sea del color de la figura
            pointerBefore = pointer
            pointer = self.move_pointer(pointer, direction)
            if self.is_valid_pointer(pointer):
                print(f"\n(71) Pointer: {pointer}\n")
                box = board_repo.get_box_by_position(board_id, pointer[0], pointer[1], db)
                box_color = box.color
                print(f"\n(73) BoxColor: {box_color}\n")
                bel_to_fig = self.belongs_to_figure(pointer, figure)
                print(f"\n(75) BelongsToFigure: {bel_to_fig}\n")
                if (box_color == color) and not bel_to_fig:
                    return False
                

            # retrotraer el pointer    
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

    def check_path_blind(self, path, pointer, board_id, color, figure_id, db):
        boardRepo = BoardRepository()

        result = True
        figure = [] # list of boxes that form the figure

        # print full path
        logging.debug(f"\n(89) Path: {path}\n")
        logging.debug(f"\n(95) BaseColor: {color}\n")

        # Agregamos la casilla inicial a la figura formada
        first_box = boardRepo.get_box_by_position(board_id, pointer[0], pointer[1], db)
        figure.append(first_box)
        
        for direction in path:
            logging.debug(f"\n(91) PathDir: {direction}\n")
            pointerBefore = pointer
            logging.debug(f"\n(93) PointerBefore: {pointer}\n")
            pointer = self.move_pointer(pointer, direction)
            logging.debug(f"\n(95) PointerAfter: {pointer}\n")
            if not self.is_valid_pointer(pointer):
                result = False
                logging.debug(f"\n(98) Result: False (invalid pointer)\n")
                break
            box = boardRepo.get_box_by_position(board_id, pointer[0], pointer[1], db)
            get_color = box.color
            logging.debug(f"\n(100) Color: {get_color}\n")
            printable_box = boardRepo.get_box_by_position(board_id, pointer[0], pointer[1], db)
            logging.debug(f"\n(101) Box: {printable_box}\n")
            if get_color != color:
                result = False
                logging.debug(f"\n(102) Result: False (invalid color)\n")
                break
            logging.debug(f"\n(104) Result: True\n")
            # Agregar la casilla a la figura formada
            new_box = boardRepo.get_box_by_position(board_id, pointer[0], pointer[1], db)
            figure.append(new_box)

        # si obtuvimos una figura valida, chequear que no sea contigua a ningun otro color de su mismo tipo
        if result:
            for fig_box in figure:
                
                if not self.check_surroundings(path, figure, (fig_box.pos_x, fig_box.pos_y), board_id, color, db):
                    return False
                
                # highlight the box in the board
                boardRepo.highlight_box(fig_box.id, db)
                boardRepo.update_figure_id_box(fig_box.id, figure_id, db)
                fig_box.highlighted = True
                
            return figure # return the figure if it is valid

        return result


    def check_path(self, path, figure, pointer, board, color, db):
        board_repo = BoardRepository()
        result = True
        print(f"\n(89) Path: {path}\n")
        # Hacer todos los chequeos para la 1er casilla de la figura
        # chequear que la casilla de la figura sea del color de la figura
        if not self.belongs_to_figure(pointer, figure):
            result = False
        # chequear que la casilla de la figura sea del color de la figura
        box = board_repo.get_box_by_position(board.board_id, pointer[0], pointer[1], db)
        get_color = box.color
        if get_color != color:
            result = False
        # chequear que las casillas de alrededor del pointer dado sean de distinto color
        check_surroundings = self.check_surroundings(path, figure, pointer, board.board_id, color, db)
        result = result and check_surroundings
        print(f"\n(167) Result for first box: {result}\n")

        for direction in path:
            # mover el pointer 
            # bug: si la figura es de mas longitud que el path - 1 
            # (esto no deberia pasar de todas maneras a no ser que se pase una figura de tipo X y longitud X con longitud Y != X)
            print(f"\n(173) Path: {direction}\n")
            print(f"\n(174) PointerBefore: {pointer}\n")
            pointer = self.move_pointer(pointer, direction)
            # Antes de seguir fijarse de que no se salga de los limites del tablero
            if not self.is_valid_pointer(pointer):
                result = False
                break
            check_surroundings = self.check_surroundings(path, figure, pointer, board.board_id, color, db)
            # check if the current pointer points to a box from our figure
            inBounds = self.belongs_to_figure(pointer, figure)
            # if not inBounds:
                # raise HTTPException(status_code=404, detail="Boxes given out of type figure bounds")
                # result = {'message': "Boxes given out of type figure bounds"}
            box = board_repo.get_box_by_position(board.board_id, pointer[0], pointer[1], db)
            get_color = box.color
            result = result and (get_color == color) and inBounds and check_surroundings
            print(f"\n(187) Result: {result}\n")

            if not result:
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
            min_x = min(box.pos_x for box in figure)
            min_x_boxes = [box for box in figure if box.pos_x == min_x]
            min_y = min(box.pos_y for box in min_x_boxes)
            x = min_x
            y = min_y
        elif rot == 1:
            max_y = max(box.pos_y for box in figure)
            max_y_boxes = [box for box in figure if box.pos_y == max_y]
            min_x = min(box.pos_x for box in max_y_boxes)
            x = min_x
            y = max_y
        elif rot == 2:
            max_x = max(box.pos_x for box in figure)
            max_x_boxes = [box for box in figure if box.pos_x == max_x]
            max_y = max(box.pos_y for box in max_x_boxes)
            x = max_x
            y = max_y
        elif rot == 3:
            min_y = min(box.pos_y for box in figure)
            min_y_boxes = [box for box in figure if box.pos_y == min_y]
            max_x = max(box.pos_x for box in min_y_boxes)
            x = max_x
            y = min_y
        else:
            raise HTTPException(status_code=404, detail="Invalid rotation")

        return (x,y)


    def check_valid_figure(self,figure,figure_type,board, db):
        pointer = self.get_pointer_from_figure(figure,0)
        board_repo = BoardRepository()
        color = board_repo.get_box_by_position(board.board_id, pointer[0], pointer[1], db)
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
            self.fig_card_repo.discard_figure_card(figureInfo.card_id, db)
            

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

    # Logica de resaltar figuras formadas

    def is_pointer_different_from_formed_figures(self, pointer, figures):
        for figure in figures:
            for fig_box in figure:
                if fig_box.pos_x == pointer[0] and fig_box.pos_y == pointer[1]:
                    return False
        return pointer
    
    def get_formed_figures(self, game_id, db):
        # clear output.log 
        open('output.log', 'w').close()
        board_repo = BoardRepository()
        
        # Chequear que el juego exista y este iniciado
        gameStateRepo = GameStateRepository()
        game = gameStateRepo.get_game_state_by_id(game_id, db)
        
        if game == None:
            raise HTTPException(status_code=404, detail="Game not found when getting formed figures")
        if game.state != "PLAYING":
            raise HTTPException(status_code=404, detail="Game not in progress when getting formed figures")
        
        # Chequear board existe
        board_id = board_repo.get_existing_board(game_id, db).id
        if board_id == None:
            raise HTTPException(status_code=404, detail="Board not found when getting formed figures")
        
        # Reset del tablero
        board_repo.reset_highlight_for_all_boxes(game_id, db)
        board_repo.reset_highlight_for_all_boxes(game_id, db)
        
        figures = []
        figure_or_bool = False
        figure_id = 0
        
        for k in range(6): # y axis 
            for l in range(6): # x axis 
                # Asignar pointer siempre y cuando sea distinto de las posiciones de las figuras ya formadas
                pointer = self.is_pointer_different_from_formed_figures((l,k), figures)
                if pointer == False:
                    continue
                box = board_repo.get_box_by_position(board_id, pointer[0], pointer[1], db)
                color = box.color
                for path in FigurePaths:
                    for i in range(4): # 4 rotaciones del path
                        figure_or_bool = self.check_path_blind(path.path, pointer, board_id, color, figure_id, db)
                        if figure_or_bool != False :
                            figures.append(figure_or_bool)
                            figure_id += 1
                            break
                        path.path = [direction_map[direction] for direction in path.path]
                    
                    if figure_or_bool != False:
                        break


def get_fig_cards_logic(fig_card_repo: FigureCardsRepository = Depends(), player_repo: PlayerRepository = Depends()):
    return FigureCardsLogic(fig_card_repo, player_repo)

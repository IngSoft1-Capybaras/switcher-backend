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
from partial_movement.partial_movement_repository import PartialMovementRepository
from movementCards.movement_cards_repository import MovementCardsRepository

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
        
        hard_cards = [card for card in typeEnum if card.name.startswith('FIG') and not card.name.startswith('FIGE')]
        easy_cards = [card for card in typeEnum if card.name.startswith('FIGE')]

        hard_cards_per_player = 36 // len(players)
        easy_cards_per_player = 14 // len(players)
        
        for player in players:
            #Random
            random.shuffle(easy_cards)
            random.shuffle(hard_cards)

            player_cards = (hard_cards[:hard_cards_per_player] + easy_cards[:easy_cards_per_player])

            random.shuffle(player_cards)

            #armo el mazo para el jugador
            show = True
            for index, figure in enumerate(player_cards):
                if index == SHOW_LIMIT:
                    show = False
                self.fig_card_repo.create_figure_card(player.id, game_id, figure, show, db)

        return {"message": "Figure deck created"}

    def is_valid_pointer(self, pointer):
        return pointer[0] >= 0 and pointer[0] <= 5 and pointer[1] >= 0 and pointer[1] <= 5

    def check_surroundings(self, path, figure, pointer, board, color, db):
        # chequear que las casillas de alrededor del pointer dado sean de distinto color
        for direction in DirectionEnum:
            # chequear que la casilla de alrededor de la figura sea del color de la figura
            pointerBefore = pointer
            pointer = self.move_pointer(pointer, direction)
            if self.is_valid_pointer(pointer):
                box = board.boxes[pointer[1]][pointer[0]]
                box_color = box.color
                bel_to_fig = self.belongs_to_figure(pointer, figure)
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

    def check_path_blind(self, path, pointer, board, color, figure_id, figure_type, db, board_figure=None):
        boardRepo = BoardRepository()
        result = True
        figure = [] # list of boxes that form the figure

        if board_figure != None:
            # check if the current pointer points to a box from our figure
            inBounds = self.belongs_to_figure(pointer, board_figure)
            if not inBounds:
                raise HTTPException(status_code=404, detail="Boxes given out of type figure bounds")
                result = False
                return result

        # Agregamos la casilla inicial a la figura formada
        first_box = board.boxes[pointer[1]][pointer[0]]
        figure.append(first_box)
        
        for direction in path:
            pointerBefore = pointer
            pointer = self.move_pointer(pointer, direction)

            if not self.is_valid_pointer(pointer):
                result = False
                break
            box = board.boxes[pointer[1]][pointer[0]]
            if box.color != color:
                result = False
                break
            if board_figure != None:
                # check if the current pointer points to a box from our figure
                if not self.belongs_to_figure(pointer, board_figure):
                    result = False
                    break
            # Agregar la casilla a la figura formada
            figure.append(box)

        # si obtuvimos una figura valida, chequear que no sea contigua a ningun otro color de su mismo tipo
        if result:
            for fig_box in figure:
                if not self.check_surroundings(path, figure, (fig_box.pos_x, fig_box.pos_y), board, color, db):
                    return False
            
            if (figure_type is not None) and (figure_id is not None):
                for fig_box in figure:
                    # highlight the box in the board
                    fig_box = boardRepo.get_box_by_position(board.board_id, fig_box.pos_x, fig_box.pos_y, db)
                    boardRepo.highlight_box(fig_box.id, db)
                    boardRepo.update_figure_id_box(fig_box.id, figure_id, figure_type, db)
                    fig_box.highlighted = True
              
            return figure # return the figure if it is valid

        return result

    def get_pointer_from_figure(self,figure, rot):
        if len(figure) == 0:
            raise HTTPException(status_code=404, detail="Empty figure")

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
        color = board.boxes[pointer[1]][pointer[0]].color
        if color != figure[0].color:
            raise HTTPException(status_code=404, detail="Color of figure does not match with color in board")
        validType = False
        result = False
        for path in FigurePaths:
            if path.type == figure_type:
                # chequear las 4 rotaciones posibles del path
                for _ in range(4):
                    # Chequear los 4 posibles puntos de referencia de la figura (depende de que tan rotada venga) 
                    for rot in range(4):
                        # Cambiar el pointer a la posición inicial de la figura rotada 90 grados j veces
                        pointer = self.get_pointer_from_figure(figure, rot)

                        partial_result = self.check_path_blind(path.path, pointer, board, color, None, None, db, figure)
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
        boardRepo.upd_box_color(board.board_id, 0, 1, "BLUE", db)
        boardRepo.upd_box_color(board.board_id, 0, 2, "BLUE", db)
        boardRepo.upd_box_color(board.board_id, 0, 3, "BLUE", db)
        boardRepo.upd_box_color(board.board_id, 1, 2, "BLUE", db)
        # boardRepo.upd_box_color(board.board_id, 3, 3, "RED", db)

        # agrego una a los surroundings para provar nueva funcion
        boardRepo.upd_box_color(board.board_id, 1, 1, "BLUE", db)
        boardRepo.upd_box_color(board.board_id, 2, 1, "BLUE", db)
        boardRepo.upd_box_color(board.board_id, 3, 1, "BLUE", db)
        # boardRepo.upd_box_color(board.board_id, 1, 5, "BLUE", db)
        # boardRepo.upd_box_color(board.board_id, 0, 5, "BLUE", db)
        # boardRepo.upd_box_color(board.board_id, 3, 2, "BLUE", db)
        # boardRepo.upd_box_color(board.board_id, 2, 2, "BLUE", db)
        # boardRepo.upd_box_color(board.board_id, 1, 3, "BLUE", db)
        # boardRepo.upd_box_color(board.board_id, 0, 3, "BLUE", db)

        return board

    async def play_figure_card(self, figureInfo, db):

        gameStateRepo = GameStateRepository()
        board_repo = BoardRepository()
        partial_repo = PartialMovementRepository()
        mov_card_repo = MovementCardsRepository()
        
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
            
            partial_repo.delete_all_partial_movements_by_player(figureInfo.player_id, db)
            mov_card_repo.discard_all_player_partially_used_cards(figureInfo.player_id, db)

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

    def has_minimum_length(self, pointer, board, color, db, min_length):
        length = 0
        queue = [pointer]
        visited = set()

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            box = board.boxes[current[1]][current[0]]
            if box.color == color:
                length += 1
                if length >= min_length:
                    return True
                for direction in DirectionEnum:
                    next_pointer = self.move_pointer(current, direction)
                    if self.is_valid_pointer(next_pointer) and next_pointer not in visited:
                        queue.append(next_pointer)
        return False

    def is_pointer_different_from_formed_figures(self, pointer, figures):
        for figure in figures:
            for fig_box in figure:
                if fig_box.pos_x == pointer[0] and fig_box.pos_y == pointer[1]:
                    return False
        return pointer
    
    async def get_formed_figures(self, game_id, db):
        # clear output.log 
        # open('output.log', 'w').close()
        board_repo = BoardRepository()
        
        # Chequear que el juego exista y este iniciado
        gameStateRepo = GameStateRepository()
        game = gameStateRepo.get_game_state_by_id(game_id, db)
        
        if game == None:
            raise HTTPException(status_code=404, detail="Game not found when getting formed figures")
        if game.state != "PLAYING":
            raise HTTPException(status_code=404, detail="Game not in progress when getting formed figures")
        
        board = board_repo.get_configured_board(game_id, db)
        if board == None:
            raise HTTPException(status_code=404, detail="Board not found when getting formed figures")
        
        # self.modifiyBoardTest(board,db)

        # Chequear board existe
        board_id = board.board_id
        if board_id == None:
            raise HTTPException(status_code=404, detail="Board not found when getting formed figures")
        
        # Reset del tablero
        board_repo.reset_highlight_for_all_boxes(game_id, db)
        board_repo.reset_figure_for_all_boxes(game_id, db)
        
        figures = []
        figure_or_bool = False
        figure_id = 0

        for i, row in enumerate(board.boxes):
            for j, box in enumerate(row):
                # Asignar pointer siempre y cuando sea distinto de las posiciones de las figuras ya formadas
                pointer = self.is_pointer_different_from_formed_figures((j,i), figures)
                print(f"\n(get_formed_figures) pointer new or false : {pointer}\n")
                if pointer == False:
                    continue
                color = box.color

                # Check if there are at least 4 blocks of the same color before applying paths
                if not self.has_minimum_length(pointer, board, color, db, min_length=4):
                    continue
                
                for path in FigurePaths:
                    for _ in range(4): # 4 rotaciones del path
                        figure_or_bool = self.check_path_blind(path.path, pointer, board, color,figure_id, path.type, db)
                        if figure_or_bool != False :
                            figures.append(figure_or_bool)
                            figure_id += 1
                            break
                        path.path = [direction_map[direction] for direction in path.path]
                    
                    if figure_or_bool != False:
                        break


def get_fig_cards_logic(fig_card_repo: FigureCardsRepository = Depends(), player_repo: PlayerRepository = Depends()):
    return FigureCardsLogic(fig_card_repo, player_repo)
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import List

from game.models import Game
from gameState.models import StateEnum
from .models import Board, Box, ColorEnum
from .schemas import BoardOut, BoardAndBoxesOut, BoxOut
import random

class BoardRepository:
    
    def get_existing_board(self, game_id: int, db: Session):
        board = db.query(Board).filter(Board.game_id == game_id).first()
        
        return BoardOut.model_validate(board) if board else None
    
    def create_new_board(self, game_id: int, db: Session):
        # Nos aseguramos que un tablero no haya sido creado TODO: Ver si es necesario
        # existing_board = self.get_existing_board(game_id, db)
        # if existing_board:
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Board already exists")
        
        # Chequeamos que el juego exista
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

        #Creamos un nuevo tablero
        new_board = Board(game_id=game_id)
        db.add(new_board)
        db.commit()
        db.refresh(new_board)

        # return new_board
        return BoardOut.model_validate(new_board) if new_board else None
        
        
    def add_box_to_board(self, board_id: int, game_id: int, color: ColorEnum, pos_x: int, pos_y: int, db: Session):
        new_box = Box(
            color=color,
            pos_x=pos_x,
            pos_y=pos_y,
            game_id=game_id,
            board_id=board_id
        )    
        db.add(new_box)
        db.commit()

    def get_configured_board(self, game_id: int, db: Session):
        """
        Get the board and its boxes of a given game

        Args:
            game_id (int): The id of the game

        Returns:
            dict: The board and its boxes in a list of lists
        """
        
        # chequear que el juego exista y este iniciado
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
        if game.game_state.state != StateEnum.PLAYING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Game not started")

        board = db.query(Board).filter(Board.game_id == game_id).first()

        if not board:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")

        # Formato Lista de listas para las filas de las casillas
        rows_in_board : List[List[BoxOut]] = []
        for index in range(6):
            # Se queda con las casillas de la fila nro index
            boxes_row = db.query(Box).filter(Box.board_id == board.id, Box.pos_y == index).all()

            if not boxes_row:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Boxes not found in row {index}")

            rows_in_board.append(boxes_row)

        if not rows_in_board:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boxes rows not found")
        
        result = BoardAndBoxesOut(game_id=board.game_id, board_id=board.id, boxes=rows_in_board)
        
        return BoardAndBoxesOut.model_validate(result)
    
    
    # preguntar si en vez de la pos pueden pasar el box_from_id y el box_pos_id
    def swap_pieces(self, game_id: int, pos_from_x: int, pos_from_y: int,   # pos_from: tuple[int, int] 
                    pos_to_x: int, pos_to_y: int, db: Session):             # pos_to: tuple[int, int]
        
        board = self.get_existing_board(game_id, db)
        
        # busco las boxes a swapear
        try:
            box_from = db.query(Box).filter(Box.game_id == game_id, Box.board_id == board.id, 
                                   Box.pos_x == pos_from_x, Box.pos_y == pos_from_y).one()
        except NoResultFound:
            raise HTTPException(status_code = 404, detail = f"Box in position {(pos_from_x, pos_from_y)} not found")

        try:
            box_to = db.query(Box).filter(Box.game_id == game_id, Box.board_id == board.id, 
                                   Box.pos_x == pos_to_x, Box.pos_y == pos_to_y).one()
        except NoResultFound:
            raise HTTPException(status_code = 404, detail = f"Box in position {(pos_to_x, pos_to_y)} not found")

        # hago el swap
        # guardo en una variable auxiliar las posicion de from
        aux_pos_from = (box_from.pos_x, box_from.pos_y)

        # cambio la pos de box_from a la de box_to
        box_from.pos_x = box_to.pos_x
        box_from.pos_y = box_to.pos_y

        # lo mismo para to con el aux_pos_from
        box_to.pos_x = aux_pos_from[0]
        box_to.pos_y = aux_pos_from[1]

        db.commit()

        

        return {"message": "The board was succesfully updated"}
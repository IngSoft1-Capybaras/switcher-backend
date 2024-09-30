from fastapi import HTTPException, status
from sqlalchemy.orm import Session
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

            
    def configure_board(self, game_id: int, db: Session):
        # Nos aseguramos que un tablero no haya sido creado
        existing_board = self.get_existing_board(game_id, db)
        
        if existing_board:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Board already exists")
        
        #Creamos un nuevo tablero
        new_board = self.create_new_board(game_id, db)
        
        #Creamos una lista con los colores de las casillas
        colors = [ColorEnum.BLUE] * 9 + [ColorEnum.GREEN] * 9 + [ColorEnum.RED] * 9 + [ColorEnum.YELLOW] * 9
        random.shuffle(colors) # le damos un orden aleatorio
        
        #Creamos cada casilla y las guardamos en la DB
        for i, color in enumerate(colors):
                pos_x = i % 6
                pos_y = i // 6
                self.add_box_to_board(new_board.id, game_id, color, pos_x, pos_y, db)
        return {"message": "Board created successfully"}

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
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boxes not found in row " . index)

            rows_in_board.append(boxes_row)

        if not rows_in_board:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Boxes rows not found")
        
        result = BoardAndBoxesOut(game_id=board.game_id, board_id=board.id, boxes=rows_in_board)
        
        return BoardAndBoxesOut.model_validate(result)
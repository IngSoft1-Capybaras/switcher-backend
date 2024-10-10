from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import List

from game.models import Game
from gameState.models import StateEnum
from .models import Board, Box, ColorEnum
from .schemas import BoardOut, BoardAndBoxesOut, BoardPosition, BoxOut

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
    
    def switch_boxes(self, game_id: int, pos_from: BoardPosition, pos_to: BoardPosition, db: Session):
        
        try:
            db.query(Game).filter(Game.id == game_id).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
        
        try:
            box_from = db.query(Box).filter(Box.game_id == game_id,
                                            Box.pos_x == pos_from[0],
                                            Box.pos_y == pos_from[1]
                                           ).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Box not found")
        
        try:
            box_to = db.query(Box).filter(Box.game_id == game_id,
                                            Box.pos_x == pos_to[0],
                                            Box.pos_y == pos_to[1]
                                           ).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Box not found")
        
        # Intercambio colores
        box_to_new_color = box_from.color
        
        box_from.color = box_to.color
        box_to.color = box_to_new_color
        
        #Guardo los cambios
        db.commit()
        
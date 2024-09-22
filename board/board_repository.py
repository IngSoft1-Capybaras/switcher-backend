from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .models import Board, Box, ColorEnum
from .schemas import BoardOut
import random

class BoardRepository:
    
    def get_existing_board(self, game_id: int, db: Session):
        
        try:
            board = db.query(Board).filter(Board.game_id == game_id).first()
        finally:
            db.close()
        return BoardOut.model_validate(board) if board else None
    
    def create_new_board(self, game_id: int, db: Session):
        
        try:
            new_board = Board(game_id=game_id)
            db.add(new_board)
            db.commit()
            db.refresh(new_board)
            return new_board
        
        finally:
            db.close()
        
    def add_box_to_board(self, board_id: int, game_id: int, color: ColorEnum, pos_x: int, pos_y: int, db: Session):

        try:
            new_box = Box(
                color=color,
                pos_x=pos_x,
                pos_y=pos_y,
                game_id=game_id,
                board_id=board_id
            )    
            db.add(new_box)
            db.commit()
            
        finally:
            db.close()
            
    def configure_board(self, game_id: int, db: Session):
        
        #Nos aseguramos que un tablero no haya sido creado
        existing_board = self.get_existing_board(game_id, db)
        
        if existing_board:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Board already exists")
        
        #Creamos un nuevo tablero
        new_board = self.create_new_board(game_id, db)
        
        #Creamos una lista con los colores de las casillas
        colors = [ColorEnum.BLUE] * 9 + [ColorEnum.GREEN] * 9 + [ColorEnum.RED] * 9 + [ColorEnum.YELLOW] * 9
        random.shuffle(colors) #le damos un orden aleatorio
        
        #Creamos cada casilla y las guardamos en la DB
        for i, color in enumerate(colors):
                pos_x = i % 6
                pos_y = i // 6
                self.add_box_to_board(new_board.id, game_id, color, pos_x, pos_y, db)
        return {"message": "Board created successfully"}
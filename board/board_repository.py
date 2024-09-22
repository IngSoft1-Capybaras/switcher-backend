from sqlalchemy.orm import sessionmaker
from .models import Board, Box, ColorEnum
from .schemas import BoardOut
from database.db import engine
import random


Session = sessionmaker(bind=engine)

class BoardRepository:
    
    def get_existing_board(self, game_id: int):
        session = Session()
        try:
            board = session.query(Board).filter(Board.id_game == game_id).first()
            if board:
                return BoardOut.model_validate(board)
        finally:
            session.close()
        
    
    def create_new_board(self, game_id: int):
        session = Session()
        try:
            new_board = Board(id_game=game_id)
            session.add(new_board)
            session.commit()
            session.refresh(new_board)
            return new_board
        
        finally:
            session.close()
        
    def add_box_to_board(self, board_id: int, game_id: int, color: ColorEnum, pos_x: int, pos_y: int):
        session = Session()
        try:
            new_box = Box(
                color=color,
                posX=pos_x,
                posY=pos_y,
                idGame=game_id,
                idBoard=board_id
            )    
            session.add(new_box)
            session.commit()
            
        finally:
            session.close()
            
    def configure_board(self, game_id: int):
        
        #Nos aseguramos que un tablero no haya sido creado
        existing_board = self.get_existing_board(game_id)
        
        if existing_board:
            return {"error": "Ya se ha creado un tablero para esta partida"}
        
        #Creamos un nuevo tablero
        new_board = self.create_new_board(game_id)
        
        #Creamos una lista con los colores de las casillas
        colors = [ColorEnum.BLUE] * 9 + [ColorEnum.GREEN] * 9 + [ColorEnum.RED] * 9 + [ColorEnum.YELLOW] * 9
        random.shuffle(colors) #le damos un orden aleatorio
        
        #Creamos cada casilla y las guardamos en la DB
        for i, color in enumerate(colors):
                pos_x = i % 6
                pos_y = i // 6
                self.add_box_to_board(new_board.id, game_id, color, pos_x, pos_y)
        return {"message": "Board created successfully"}
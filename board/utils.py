import random
from sqlalchemy.orm import Session
from .models import Board, Box, ColorEnum

def create_board(session: Session, game_id: int):
    #Nos aseguramos que un tablero no haya sido creado
    existing_board = session.query(Board).filter(Board.id_game == game_id).first()
    if existing_board:
        return {"error": "Ya se ha creado un tablero para esta partida"}
    
    
    #Creamos un nuevo tablero
    new_board = Board(id_game= game_id)
    
    #Guardar el nuevo tablero en la DB
    session.add(new_board)
    session.commit()
    session.refresh(new_board)
    
    #Creamos una lista con los colores de las casillas
    colors = [ColorEnum.BLUE] * 9 + [ColorEnum.GREEN] * 9 + [ColorEnum.RED] * 9 + [ColorEnum.YELLOW] * 9
    random.shuffle(colors) #le damos un orden aleatorio
    
    #Creamos cada casilla y las guardamos en la DB
    for i, color in enumerate(colors):
        posX = i % 6
        posY = i // 6
        new_box = Box(
            color = color, 
            posX = posX,
            posY = posY,
            idGame = game_id,
            idBoard = new_board.id
        )
        session.add(new_box)
        
    session.commit()
    return {"message": "Board created succesfully"}
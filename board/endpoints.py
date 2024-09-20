import random
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from .models import Board, Box
from .schemas import BoxOut



board_router = APIRouter(
    prefix="/board",
    tags=['Board']
)

@board_router.get("/{game_id}", status_code=status.HTTP_200_OK)
async def get_game_board(game_id: int, db: Session = Depends(get_db)):
    
    #Nos aseguramos que el tablero exista:
    board = db.query(Board).filter(Board.id_game == game_id).first()
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No board for game of id {game_id}")

    #Si existe obtenemos los elementos del mismo
    boxes = db.query(Box).filter(Box.idBoard == board.id).all()
    if not boxes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No boxes found for board of id {board.id}")
    
    boxes_data = [BoxOut.model_validate(box) for box in boxes]
    
    return {"board" : boxes_data}

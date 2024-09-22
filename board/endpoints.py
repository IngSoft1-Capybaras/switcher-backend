import random
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from .models import Board, Box
from .schemas import BoxOut
from .board_repository import BoardRepository

board_router = APIRouter(
    prefix="/board",
    tags=['Board']
)

#NO SUBIR A DEV , ENDPOINT DE FACU
@board_router.get("/{game_id}", status_code=status.HTTP_200_OK)
async def get_game_board(game_id: int, db: Session = Depends(get_db), board_repo: BoardRepository = Depends() ):
    
    #Nos aseguramos que el tablero exista:
    board = board_repo.get_existing_board(game_id)
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No board for game of id {game_id}")

    #Si existe obtenemos los elementos del mismo
    boxes = db.query(Box).filter(Box.board_id == board.id).all()
    if not boxes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No boxes found for board of id {board.id}")
    
    boxes_data = [BoxOut.model_validate(box) for box in boxes]
    
    return {"board" : boxes_data}

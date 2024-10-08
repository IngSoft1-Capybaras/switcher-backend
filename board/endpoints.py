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

@board_router.get("/{game_id}")
async def get_board(game_id: int, db: Session = Depends(get_db), repo: BoardRepository = Depends()):
    return repo.get_configured_board(game_id, db)
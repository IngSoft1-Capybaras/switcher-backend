from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from .movement_cards_repository import MovementCardsRepository

movement_cards_router = APIRouter()

# Obtener cartas de figura
@movement_cards_router.get("/deck/figure/{game_id}/{player_id}")
async def get_movement_cards(player_id: int, game_id: int, db: Session = Depends(get_db), repo: MovementCardsRepository = Depends()):
    return repo.get_movement_cards(player_id, game_id, db)
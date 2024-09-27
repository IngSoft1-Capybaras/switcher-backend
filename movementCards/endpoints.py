from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from .movement_cards_repository import MovementCardsRepository

movement_cards_router = APIRouter()

# Obtener cartas de movimiento
@movement_cards_router.get("/deck/movement/{game_id}/{player_id}")
async def get_movement_cards(game_id: int, player_id: int, db: Session = Depends(get_db), repo: MovementCardsRepository = Depends()):
    return repo.get_movement_cards(game_id, player_id, db)

# Obtener todas las cartas de movimiento
@movement_cards_router.get("/deck/movement/{game_id}/{player_id}/{card_id}")
async def get_movement_cards(game_id: int, player_id: int, card_id: int, db: Session = Depends(get_db), repo: MovementCardsRepository = Depends()):
    return repo.get_movement_card_by_id(game_id, player_id, card_id, db)
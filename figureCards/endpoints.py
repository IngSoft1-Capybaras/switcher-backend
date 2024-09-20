from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from .models import FigureCard
from player.models import Player
from game.models import Game
from database.db import get_db
from .figure_cards_repository import FigureCardsRepository

figure_cards_router = APIRouter()

# Obtener cartas de figura
@figure_cards_router.get("/deck/figure/{game_id}/{player_id}")
async def get_figure_cards(player_id: int, game_id: int, db: Session = Depends(get_db), repo: FigureCardsRepository() = Depends()):
    return repo.get_figure_cards(player_id, game_id, db)

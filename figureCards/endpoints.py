from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from .figure_cards_repository import FigureCardsRepository, get_figure_cards_repository
from game.game_logic import GameLogic, get_game_logic

figure_cards_router = APIRouter()

# Obtener todas las cartas de figura
@figure_cards_router.get("/deck/figure/{game_id}/{player_id}")
async def get_figure_cards(game_id: int, player_id: int, 
                           db: Session = Depends(get_db), 
                           repo: FigureCardsRepository = Depends(get_figure_cards_repository)):
    
    return repo.get_figure_cards(game_id, player_id, db)


# Obtener una carta de figura especifica
@figure_cards_router.get("/deck/figure/{game_id}/{player_id}/{card_id}")
async def get_figure_card_by_id(game_id: int, player_id: int, 
                                card_id: int, db: Session = Depends(get_db), 
                                repo: FigureCardsRepository = Depends(get_figure_cards_repository)):
    
    return repo.get_figure_card_by_id(game_id, player_id, card_id, db)


# Jugar una carta de figura
@figure_cards_router.post("/deck/figure/discard_card")
async def discard_figure_card(game_id: int, player_id: int, 
                              card_id: int, db: Session = Depends(get_db), 
                              repo: FigureCardsRepository = Depends(get_figure_cards_repository), 
                              game_logic: GameLogic = Depends(get_game_logic)):
    
    res = repo.discard_figure_card(game_id, player_id, card_id, db)

    await game_logic.check_win_condition(game_id, player_id, db)

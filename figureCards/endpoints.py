from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from .figure_cards_repository import FigureCardsRepository, get_figure_cards_repository
from .figure_cards_logic import FigureCardsLogic, get_fig_cards_logic
from game.game_logic import GameLogic, get_game_logic
from .schemas import PlayFigureCardInput

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
@figure_cards_router.post("/deck/figure/play_card")
async def play_figure_card(figureInfo: PlayFigureCardInput, logic: FigureCardsLogic = Depends(get_fig_cards_logic), db: Session = Depends(get_db)):

    return await logic.play_figure_card(figureInfo, db)
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from .figure_cards_repository import FigureCardsRepository, get_figure_cards_repository
from .figure_cards_logic import FigureCardsLogic, get_fig_cards_logic
from game.game_logic import GameLogic, get_game_logic
from .schemas import PlayFigureCardInput
from connection_manager import manager

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


# bloquear una carta de figura
@figure_cards_router.post("/deck/figure/{game_id}/{player_id}/{figure_card_id}/block_card", status_code = status.HTTP_201_CREATED)
async def block_figure_card(game_id: int, player_id: int, figure_card_id: int, repo: FigureCardsRepository = Depends(get_figure_cards_repository), 
                            logic: FigureCardsLogic = Depends(get_fig_cards_logic), db: Session = Depends(get_db)):
    valid = logic.check_valid_block(game_id, player_id, figure_card_id, db)
    if valid:
        message = {"type": f"{game_id}:BLOCK_CARD"}
        await manager.broadcast(message)

        return repo.block_figure_card(game_id, figure_card_id, db)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid blocking")
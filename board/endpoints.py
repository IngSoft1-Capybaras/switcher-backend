import random

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.db import get_db
from figureCards.figure_cards_logic import (FigureCardsLogic,
                                            get_fig_cards_logic)
from figureCards.figure_cards_repository import (FigureCardsRepository,
                                                 get_figure_cards_repository)
from player.player_repository import PlayerRepository

from .board_logic import BoardLogic
from .board_repository import BoardRepository
from .models import Board, Box
from .schemas import BoardAndBoxesOut, BoxOut

board_router = APIRouter(
    prefix="/board",
    tags=['Board']
)

@board_router.get("/{game_id}")
async def get_board(game_id: int, db: Session = Depends(get_db), repo: BoardRepository = Depends()):
    # obtener figuras formadas
    figRepo = FigureCardsRepository()
    playerRepo = PlayerRepository()
    figLogic = FigureCardsLogic(figRepo, playerRepo)
    formed_figures = figLogic.get_formed_figures(game_id, db)
    result = repo.get_configured_board(game_id, db)
    result_dict = result.dict()
    result_dict["formed_figures"] = formed_figures
    return BoardAndBoxesOut(**result_dict)
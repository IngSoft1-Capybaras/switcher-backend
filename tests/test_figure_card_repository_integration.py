import pytest
from sqlalchemy.orm import sessionmaker
from figureCards.figure_cards_repository import FigureCardsRepository
from board.models import  Board, Box
from figureCards.models import FigureCard, typeEnum
from game.models import Game
from gameState.models import GameState
from movementCards.models import MovementCard
from player.models import Player

from database.db import engine

#Configuración de la sesión
Session = sessionmaker(bind=engine)



@pytest.fixture
def figure_cards_repository():
    return FigureCardsRepository()

@pytest.mark.integration_test
def test_create_new_figure_card(figure_cards_repository: FigureCardsRepository):
    session = Session()
    
    try:
        N_cards = session.query(FigureCard).filter(FigureCard.player_id == 17).count()
    finally:
        session.close()
    
    figure_cards_repository.create_figure_card(17,1,typeEnum.TYPE_4, session)
    
    session = Session()
    
    try:
        assert session.query(FigureCard).filter(FigureCard.player_id == 17).count() == N_cards + 1
    finally:
        session.close()
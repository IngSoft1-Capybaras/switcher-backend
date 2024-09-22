import pytest
from sqlalchemy.orm import sessionmaker
from .figure_cards_repository import FigureCardsRepository
from board.models import  Board, Box
from figureCards.models import FigureCard, typeEnum
from game.models import Game
from gameState.models import GameState
from movementCards.models import MovementCard
from player.models import Player

from database.db import engine, Base
import os

#Configuración de la sesión
Session = sessionmaker(bind=engine)

@pytest.fixture(scope='session', autouse=True)
def setup_and_teardown_db():
    # Create all tables 
    Base.metadata.create_all(engine)
    yield
    # Drop all tables after  tests
    Base.metadata.drop_all(engine)
    
    if os.path.exists("db_test.sqlite"):
        os.remove("db_test.sqlite")


@pytest.fixture
def figure_cards_repository():
    return FigureCardsRepository()


def test_create_new_figure_card(figure_cards_repository: FigureCardsRepository):
    session = Session()
    
    try:
        N_cards = session.query(FigureCard).filter(FigureCard.player_id == 1).count()
    finally:
        session.close()
    
    figure_cards_repository.create_figure_card(1,1,typeEnum.TYPE_4, db)
    
    session = Session()
    
    try:
        assert session.query(FigureCard).filter(FigureCard.player_id == 1).count() == N_cards + 1
    finally:
        session.close()
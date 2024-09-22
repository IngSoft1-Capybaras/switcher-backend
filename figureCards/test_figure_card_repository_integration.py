import pytest
from sqlalchemy.orm import sessionmaker
from .figure_card_repository import FigureCardRepository
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
def figure_card_repository():
    return FigureCardRepository()


def test_create_new_figure_card(figure_card_repository: FigureCardRepository):
    session = Session()
    
    try:
        N_cards = session.query(FigureCard).filter(FigureCard.idPlayer == 1).count()
    finally:
        session.close()
    
    figure_card_repository.create_figure_card(1,1,typeEnum.TYPE_4)
    
    session = Session()
    
    try:
        assert session.query(FigureCard).filter(FigureCard.idPlayer == 1).count() == N_cards + 1
    finally:
        session.close()
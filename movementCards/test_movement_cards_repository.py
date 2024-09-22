import pytest
from sqlalchemy.orm import sessionmaker
from .movement_cards_repository import MovementCardsRepository
from board.models import  Board, Box
from figureCards.models import FigureCard
from game.models import Game
from gameState.models import GameState
from movementCards.models import MovementCard, typeEnum
from figureCards.models import FigureCard
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
def movement_card_repository():
    return MovementCardsRepository()


def test_create_new_movement_card(movement_card_repository: MovementCardsRepository):
    session = Session()
    
    try:
        N_cards = session.query(MovementCard).filter(MovementCard.game_id == 1).count()
    finally:
        session.close()
    
    movement_card_repository.create_movement_card(1, typeEnum.EN_L_DER)
    
    session = Session()
    
    try:
        assert session.query(MovementCard).filter(MovementCard.game_id == 1).count() == N_cards + 1
    finally:
        session.close()
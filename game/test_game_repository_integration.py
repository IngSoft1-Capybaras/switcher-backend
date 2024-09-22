import pytest
from sqlalchemy.orm import sessionmaker
from .game_repository import GameRepository
from figureCards.models import FigureCard
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
def game_repository():
    return GameRepository()


def test_get_game_by_id(game_repository: GameRepository):
    session = Session()
    
    try:
        
        game = Game(
            name = "test_game",
            maxPlayers = 3,
            minPlayers = 2
        )
        session.add(game)
        session.commit()
        
        game = game_repository.get_game_by_id(1)
        assert game.id == 1
        
    finally:
        session.close()

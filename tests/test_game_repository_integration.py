import pytest
from sqlalchemy.orm import sessionmaker
from game.game_repository import GameRepository
from figureCards.models import FigureCard
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
def game_repository():
    return GameRepository()

@pytest.mark.integration_test
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
        
        game = game_repository.get_game_by_id(1, session)
        assert game.id == 1
        
    finally:
        session.close()

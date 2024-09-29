import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from game.game_repository import GameRepository
from figureCards.models import FigureCard
from board.models import  Board, Box
from figureCards.models import FigureCard, typeEnum
from game.models import Game
from game.schemas import GameCreate
from gameState.models import GameState
from movementCards.models import MovementCard
from player.models import Player
from player.schemas import PlayerCreateMatch

from database.db import engine

#Configuración de la sesión
Session = sessionmaker(bind=engine)


@pytest.fixture
def game_repository():
    return GameRepository()

@pytest.mark.integration_test
def test_get_games(game_repository: GameRepository, session):
    # session = Session()
    # try:
    N_games = session.query(Game).count()

    list_of_games = game_repository.get_games(session)

    assert len(list_of_games) == min(5, N_games)
    # finally:
    #     session.close()


@pytest.mark.integration_test
def test_get_game_by_id(game_repository: GameRepository, session):
    # session = Session()
    try:
        test_game = session.query(Game).filter(Game.id == 1).one()

        game = game_repository.get_game_by_id(1, session)

        assert game.get('id') == test_game.id
    except NoResultFound:
        raise ValueError("There is no game with id 1")
    # finally:
    #     session.close()


@pytest.mark.integration_test
def test_create_game(game_repository: GameRepository, session):
    # session = Session()

    # try:
    N_games = session.query(Game).count()

    game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    
    assert session.query(Game).count() == N_games + 1

    # finally:
    #     session.close()
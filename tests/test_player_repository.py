import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound

from fastapi import HTTPException

from player.player_repository import PlayerRepository
from game.game_repository import GameRepository

from game.models import Game
from game.schemas import GameCreate
from gameState.models import GameState, StateEnum

from player.models import Player, turnEnum
from player.schemas import PlayerCreateMatch

from database.db import engine

#Configuración de la sesión
Session = sessionmaker(bind=engine)


@pytest.fixture
def player_repo():
    return PlayerRepository()

@pytest.fixture
def game_repository():
    return GameRepository()



@pytest.mark.integration_test
def test_get_player_by_id(player_repo: PlayerRepository, session):
    # session = Session()
    try:
        test_player = session.query(Player).filter(Player.game_id == 1,
                                                   Player.id == 1).one()

        player_in_db = player_repo.get_player_by_id(1, 1, session)

        assert player_in_db.id == test_player.id
    except NoResultFound:
        raise ValueError("There is no player with id=1 in game with id=1")
    # finally:
    #     session.close()


@pytest.mark.integration_test
def test_get_players_in_game(player_repo: PlayerRepository, session):
    # session = Session()
    # try:
    N_players = session.query(Player).filter(Player.game_id == 1).count()

    players_in_game = player_repo.get_players_in_game(1, session)

    assert len(players_in_game) == N_players

    # finally:
    #     session.close()

@pytest.mark.integration_test     
def test_assign_turn_player(game_repository: GameRepository, player_repo: PlayerRepository, session):
    # session = Session()
    
    res = game_repository.create_game(GameCreate(name="Test Player Game", max_players=4, min_players=2), 
                                      PlayerCreateMatch(name="Test Player"), 
                                      session)
    
    game = res.get('game')
    player = res.get('player')

    player_repo.assign_turn_player(game.id, player.id, turnEnum.SEGUNDO, session)
        
    updated_player = session.query(Player).filter(Player.id == player.id).one()
        
    assert updated_player.turn == turnEnum.SEGUNDO


@pytest.mark.integration_test
def test_create_player_success(player_repo: PlayerRepository,game_repository: GameRepository, session):
    res = game_repository.create_game(GameCreate(name="Test Game", max_players=4, min_players=2), 
                                      PlayerCreateMatch(name="Test Player"), 
                                      session)
    
    game = res.get('game')

    player_data = player_repo.create_player(game_id=game.id, player_name="Test Player", db=session)

    new_player = session.query(Player).filter(Player.id == player_data["player_id"]).first()

    assert new_player is not None
    assert new_player.name == "Test Player"
    assert new_player.host is False
    assert new_player.winner is False
    
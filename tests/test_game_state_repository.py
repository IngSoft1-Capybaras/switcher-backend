import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from gameState.game_state_repository import GameStateRepository

from gameState.models import GameState, StateEnum

from database.db import engine

#Configuración de la sesión
Session = sessionmaker(bind=engine)


@pytest.fixture
def game_state_repository():
    return GameStateRepository()

        
@pytest.mark.integration_test
def test_get_game_state_by_id(game_state_repository: GameStateRepository, session):
    # session = Session()
    try:
        test_game_state = session.query(GameState).filter(GameState.game_id == 1).one()
        game_state = game_state_repository.get_game_state_by_id(1, session)

        assert test_game_state.id == game_state.id
    except NoResultFound:
        ValueError("There is no game state for game 1")
    # finally:
    #     session.close()


@pytest.mark.integration_test
def test_update_game_state(game_state_repository: GameStateRepository, session):
    # session = Session()
    # try:
    game_state_repository.update_game_state(1, StateEnum.PLAYING, session)
    game_state = game_state_repository.get_game_state_by_id(1, session)
    
    assert game_state.state == StateEnum.PLAYING
    # finally:
    #     session.close()


@pytest.mark.integration_test
def test_update_current_player(game_state_repository: GameStateRepository, session):
    # session = Session()
    try:
        game_state_repository.update_current_player(game_id=3, first_player_id=2, db=session)
        
        updated_game_state = session.query(GameState).filter(GameState.game_id == 3).one()
        
        assert updated_game_state.current_player == 2
    except NoResultFound:
        raise ValueError("Error fetching game state of game 3")
    # finally:
    #     session.close()


@pytest.mark.integration_test
def test_get_next_player_id(game_state_repository: GameStateRepository, session):
    # session = Session()
    # try:
        # game_id = 4
        # current_player_id = 1
        # game_state = GameState(game_id=game_id, state=StateEnum.PLAYING, current_player=current_player_id)
        
        # players = [
        #     Player(name = "player1", game_id=game_id, turn=turnEnum.PRIMERO, host=False),
        #     Player(name = "player2", game_id=game_id, turn=turnEnum.TERCERO, host=True),
        #     Player(name = "player3", game_id=game_id, turn=turnEnum.SEGUNDO, host=False)
        # ]
        
        # session.add(game_state)
        # session.add_all(players)
        # session.commit()

    test_game_state = session.query(GameState).filter(GameState.game_id == 1,
                                                        GameState.id == 1).one()
    
    current_player_id = test_game_state.current_player


    result = game_state_repository.get_next_player_id(1, session)
    
    assert result == 2
        
    # finally:
    #     session.close()
        

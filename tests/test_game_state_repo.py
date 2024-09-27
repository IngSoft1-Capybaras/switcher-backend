import pytest
from sqlalchemy.orm import sessionmaker
from gameState.game_state_repo import GameStateRepository
from board.models import Board, Box

from figureCards.models import FigureCard
from game.models import Game
from gameState.models import GameState, StateEnum
from movementCards.models import MovementCard

from player.models import Player, turnEnum


from database.db import engine, Base
import os

#Configuración de la sesión
Session = sessionmaker(bind=engine)

# @pytest.fixture(scope='session', autouse=True)
# def setup_and_teardown_db():
#     # Create all tables 
#     Base.metadata.create_all(engine)
#     yield
#     # Drop all tables after  tests
#     Base.metadata.drop_all(engine)
    
#     if os.path.exists("db_test.sqlite"):
#         os.remove("db_test.sqlite")


@pytest.fixture
def game_state_repository():
    return GameStateRepository()

        
@pytest.mark.integration_test
def test_get_game_state_by_id(game_state_repository: GameStateRepository):
    session = Session()
    
    try:
        new_game_state = GameState(
            state = StateEnum.WAITING,
            game_id = 2
        )
        session.add(new_game_state)
        session.commit()
        
        game_state = game_state_repository.get_game_state_by_id(2, session)
        assert game_state  is not None
    finally:
        session.close()


def test_update_game_state(game_state_repository: GameStateRepository):
    session = Session()
    
    try:
        game_state_repository.update_game_state(1, StateEnum.PLAYING, session)
        game_state = game_state_repository.get_game_state_by_id(1, session)
        
        assert game_state.state is StateEnum.PLAYING
    finally:
        session.close()

def test_update_current_player(game_state_repository: GameStateRepository):
    session = Session()
    
    try:
        game_state = GameState(
            game_id=3,
            state= StateEnum.WAITING, 
            current_player=0
        )
        session.add(game_state)
        session.commit()
        
        game_state_repository.update_current_player(game_id=3, first_player_id=2, db=session)
        
        updated_game_state = session.query(GameState).filter(GameState.game_id == 3).first()
        
        assert updated_game_state.current_player == 2
        
    finally:
        session.close()
        
def test_get_next_player_id(game_state_repository: GameStateRepository):
    session = Session()
    
    try:
        game_id = 4
        current_player_id = 1
        game_state = GameState(game_id=game_id, state=StateEnum.PLAYING, current_player=current_player_id)
        
        players = [
            Player(name = "player1", game_id=game_id, turn=turnEnum.PRIMERO, host=False),
            Player(name = "player2", game_id=game_id, turn=turnEnum.TERCERO, host=True),
            Player(name = "player3", game_id=game_id, turn=turnEnum.SEGUNDO, host=False)
        ]
        
        session.add(game_state)
        session.add_all(players)
        session.commit()
        
        result = game_state_repository.get_next_player_id(game_id, session)
        
        assert result == 3
        
    finally:
        session.close()
        

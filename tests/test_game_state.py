import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from gameState.game_state_repository import GameStateRepository
from player.player_repository import PlayerRepository
from game.game_repository import GameRepository
from board.board_repository import BoardRepository

from player.utils import PlayerUtils
from figureCards.utils import FigureCardUtils
from movementCards.utils import MovementCardUtils

from gameState.models import StateEnum
from player.schemas import turnEnum, PlayerInDB
from movementCards.schemas import MovementCardSchema, typeEnum

from database.db import get_db
from main import app 


client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_player_repo():
    return MagicMock(spec=PlayerRepository)

@pytest.fixture
def mock_player_utils():
    return MagicMock(spec=PlayerUtils)

@pytest.fixture
def mock_game_state_repo():
    return MagicMock(spec=GameStateRepository)

@pytest.fixture
def mock_board_repo():
    return MagicMock(spec=BoardRepository)

@pytest.fixture
def mock_movement_cards_utils():
    return MagicMock(spec=MovementCardUtils)

@pytest.fixture
def mock_figure_cards_utils():
    return MagicMock(spec=FigureCardUtils)


# Apply the override before running the tests
@pytest.fixture(autouse=True)
def setup_dependency_override(mock_player_repo, mock_board_repo, mock_figure_cards_utils, mock_game_state_repo, mock_movement_cards_utils, mock_player_utils, mock_db):
    def override_get_db():
        return mock_db
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[GameStateRepository] = lambda: mock_game_state_repo
    app.dependency_overrides[PlayerRepository] = lambda: mock_player_repo
    app.dependency_overrides[BoardRepository] = lambda: mock_board_repo
    
    app.dependency_overrides[FigureCardUtils] = lambda: mock_figure_cards_utils
    app.dependency_overrides[MovementCardUtils] = lambda: mock_movement_cards_utils
    app.dependency_overrides[PlayerUtils] = lambda: mock_player_utils
    
    yield
    app.dependency_overrides = {}  # Clean up overrides after test


def test_game_start(mock_board_repo, mock_game_state_repo, mock_player_repo, mock_figure_cards_utils, mock_movement_cards_utils, mock_player_utils, mock_db):
    game_id = 3
    game_state_id = 3
    players = [
        PlayerInDB(id=1, name="Player1", turn=turnEnum.PRIMERO, game_id=game_id, game_state_id=game_state_id, host=True, winner=False),
        PlayerInDB(id=2, name="Player2", turn=turnEnum.PRIMERO, game_id=game_id, game_state_id=game_state_id, host=False, winner=False)
    ]
    
    mock_mov_card_repo = MagicMock()
    mock_movement_cards_utils.mov_card_repo = mock_mov_card_repo
    
    mock_player_repo.get_players_in_game.return_value = players
    mock_player_utils.assign_random_turns.return_value = players[0].id
    mock_board_repo.configure_board.return_value = {"message": "Board created successfully"}
    mock_movement_cards_utils.create_mov_deck.return_value = {"message": "Movement deck created and assigned to players"}
    mock_figure_cards_utils.create_fig_deck.return_value = {"message": "Figure deck created"}
    mock_game_state_repo.update_game_state.return_value = None
    mock_game_state_repo.update_current_player.return_value = None

    # Mocking movement deck cards
    mock_movement_cards_utils.mov_card_repo.get_movement_deck.return_value = [
        MovementCardSchema(id=1, type=typeEnum.DIAGONAL_CONT, description="test", used=True, player_id=None, game_id=game_id),
        MovementCardSchema(id=2, type=typeEnum.EN_L_DER, description="test", used=False, player_id=None, game_id=game_id),
        MovementCardSchema(id=3, type=typeEnum.LINEAL_CONT, description="test", used=False, player_id=None, game_id=game_id)
    ]
    
    # Patch random.shuffle and random.sample
    with patch('figureCards.utils.random.shuffle', lambda x: x), \
         patch('figureCards.utils.random.sample', lambda x, y: x[:y]), \
         patch('movementCards.utils.random.shuffle', lambda x: x), \
         patch('movementCards.utils.random.sample') as mock_mov_random_sample :

        
        # Mock `movementCards.utils.random.sample`
        mock_mov_random_sample.return_value = [
            MovementCardSchema(id=1, type=typeEnum.DIAGONAL_CONT, description="test", used=True, player_id=1, game_id=1),
            MovementCardSchema(id=2, type=typeEnum.EN_L_DER, description="test", used=False, player_id=1, game_id=1),
            MovementCardSchema(id=3, type=typeEnum.EN_L_DER, description="test", used=False, player_id=1, game_id=1)
        ]
        
        # Debug statement to verify the mock
        print("mock_mov_random_sample.return_value:", mock_movement_cards_utils.mov_card_repo.get_movement_deck.return_value)

        with client.websocket_connect("/ws") as websocket:
            response = client.patch(f"game_state/start/{game_id}")
            
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == {"message": "Game status updated, ur playing!"}
            
            game_state_update = websocket.receive_json()
            assert game_state_update["type"] == f"{game_id}:GAME_STARTED"
            
            mock_player_repo.get_players_in_game.assert_called_with(game_id, mock_db)
            mock_figure_cards_utils.create_fig_deck.assert_called_once_with(mock_db, game_id)
            mock_movement_cards_utils.create_mov_deck.assert_called_once_with(game_id, mock_db)
            mock_player_utils.assign_random_turns.assert_called_once_with(players, mock_db)
            mock_game_state_repo.update_game_state.assert_called_once_with(game_id, StateEnum.PLAYING, mock_db)
            mock_game_state_repo.update_current_player.assert_called_once_with(game_id, players[0].id, mock_db)

    
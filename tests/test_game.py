import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy.orm import Session
from player.schemas import turnEnum
from game.game_repository import GameRepository
from game.models import Game
from game.schemas import GameInDB, GameCreate
from database.db import get_db
from main import app 


client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


# Mock repository
@pytest.fixture
def mock_repo():
    return MagicMock(spec=GameRepository)


# Apply the override before running the tests
@pytest.fixture(autouse=True)
def setup_dependency_override(mock_repo, mock_db):
    def override_get_db():
        return mock_db
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[GameRepository] = lambda: mock_repo
    yield
    app.dependency_overrides = {}  # Clean up overrides after test

# @patch('app.GameRepository')
# def test_create_game(mock_db, mock_repo):
    
    
#     response = client.post("/games", json={"game": game_data.model_dump(), "player": player_data.model_dump()})
    
#     assert response.status_code == 201
#     assert response.json() == expected_response.model_dump()
#     mock_repo.create_game.assert_called_once_with(game_data, player_data, mock_db)


def test_get_games_success(mock_repo, mock_db):
    mock_games = [
        GameCreate(name="Test game 1", max_players=4, min_players=2),
        GameCreate(name="Test game 2", max_players=4, min_players=2)
    ]

    mock_repo.get_games.return_value = mock_games
        
    response = client.get("/games")
    assert response.status_code == 200
    assert response.json() == [game.model_dump() for game in mock_games]
    mock_repo.get_games.assert_called_once_with(mock_db)


def test_get_games_not_found(mock_repo, mock_db):
    mock_repo.get_games.side_effect = HTTPException(
        status_code=404, 
        detail="There are no games available"
    )

    response = client.get("/games")

    assert response.status_code == 404
    assert response.json() == {"detail": "There are no games available"}
    mock_repo.get_games.assert_called_once_with(mock_db)


def test_get_game_by_id_success(mock_repo, mock_db):
    mock_game = GameCreate(name="test game", max_players=4, min_players=2)

    mock_repo.get_game_by_id.return_value = mock_game
    
    response = client.get(f"/games/1")
    
    assert response.status_code == 200
    assert response.json() == mock_game.model_dump()
    mock_repo.get_game_by_id.assert_called_once_with(1, mock_db)



def test_get_game_by_id_not_found(mock_repo, mock_db):
    mock_repo.get_game_by_id.side_effect = HTTPException(
        status_code = 404,
        detail = "Game not found"
    )
    
    response = client.get(f"/games/999")
    
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}
    mock_repo.get_game_by_id.assert_called_once_with(999, mock_db)


# def test_get_game_winner(mock_GameRepository, player_a):
#     pass


# def test_get_game_winner_no_winner(mock_GameRepository):
#     pass
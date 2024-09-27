import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from main import app 
from player.schemas import turnEnum
from game.endpoints import game_router

app.include_router(game_router)
client = TestClient(app)

@pytest.fixture
def game_a():
    return {
        "id": 1,
        "name": "test_game_a",
        "max_players": 4,
        "min_players": 2
    } 

@pytest.fixture
def game_b():
    return {
        "id": 2,
        "name": "test_game_b",
        "max_players": 4,
        "min_players": 2
    } 

@pytest.fixture
def player_a():
    return {
        "id": 1,
        "name": "test_player_winner",
        "game_id": 1,
        "game_state_id": 1,
        "turn": turnEnum.PRIMERO,
        "host": True,
        "winner": True
    }

@pytest.fixture
def player_b():
    return {
        "id": 1,
        "name": "test_player_loser",
        "game_id": 2,
        "game_state_id": 2,
        "turn": turnEnum.PRIMERO,
        "host": True,
        "winner": False
    }

# @patch('app.GameRepository')
# def test_create_game(mock_db, mock_repo):
    
    
#     response = client.post("/games", json={"game": game_data.model_dump(), "player": player_data.model_dump()})
    
#     assert response.status_code == 201
#     assert response.json() == expected_response.model_dump()
#     mock_repo.create_game.assert_called_once_with(game_data, player_data, mock_db)


@patch('game.game_repository.GameRepository')
def test_get_games(mock_GameRepository, game_a, game_b):
    mock_repository = MagicMock()
    mock_repository.get_games.return_value = [game_a, game_b]
    mock_GameRepository.return_value = mock_repository
        
    response = client.get("/games")
    assert response.status_code == 200
    assert response.json() == [game_a, game_b]


@patch('game.game_repository.GameRepository')
def test_get_game_by_id(mock_GameRepository, game_a):
    mock_repository = MagicMock()
    mock_repository.get_games.return_value = game_a
    mock_GameRepository.return_value = mock_repository
    
    response = client.get(f"/games/1")
    
    assert response.status_code == 200
    assert response.json() == game_a


@patch('game.game_repository.GameRepository')
def test_get_game_by_id_not_found(mock_GameRepository):
    mock_repository = MagicMock()
    mock_repository.get_games.return_value = ValueError
    mock_GameRepository.return_value = mock_repository
    
    response = client.get(f"/games/9999")
    
    assert response.status_code == 404
    assert response.json() == {"detail": "Game not found"}


@patch('game.game_repository.GameRepository')
def test_get_game_winner(mock_GameRepository, player_a):
    mock_repository = MagicMock()
    mock_repository.get_winner.return_value = player_a
    mock_GameRepository.return_value = mock_repository
    
    response = client.get(f"/games/1/winner")
    
    assert response.status_code == 200
    assert response.json() == player_a


@patch('game.game_repository.GameRepository')
def test_get_game_winner_no_winner(mock_GameRepository):
    mock_repository = MagicMock()
    mock_repository.get_games.return_value = ValueError
    mock_GameRepository.return_value = mock_repository
    
    response = client.get(f"/games/2/winner")
    
    assert response.status_code == 404
    assert response.json() == {"detail": "There is no winner"}

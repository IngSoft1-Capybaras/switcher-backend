import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status

from sqlalchemy.orm import Session
from database.db import get_db

from player.player_repository import PlayerRepository
from player.schemas import PlayerJoinRequest
from player.endpoints import player_router

from game.game_repository import GameRepository, get_game_repository
from game.schemas import GameInDB
from game.game_logic import get_game_logic, GameLogic

from main import app 

app.include_router(player_router)
client = TestClient(app)


# Mock database
@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_game_logic():
    return MagicMock(spec=GameLogic)

# Mock repository
@pytest.fixture
def player_repo():
    return MagicMock(spec=PlayerRepository)

# Mock repository
@pytest.fixture
def game_repo():
    return MagicMock(spec=GameRepository)

@pytest.fixture(autouse=True)
def setup_dependency_override(game_repo, player_repo, mock_game_logic, mock_db):
    def override_get_db():
        return mock_db
    
    def override_get_game_logic():
        return mock_game_logic
    
    def override_get_game_repository():
        return game_repo
    
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_game_logic] = override_get_game_logic
    app.dependency_overrides[PlayerRepository] = lambda: player_repo
    app.dependency_overrides[GameRepository] = lambda: game_repo
    app.dependency_overrides[get_game_repository] = override_get_game_repository

    yield
    app.dependency_overrides = {}  # Clean up overrides after test

def test_get_players_in_game(player_repo, mock_db):
    game_id = 1
    expected_players = [
        {
            "id": 1,
            "name": "Player1",
            "turn": "PRIMERO",
            "game_id": game_id,
            "game_state_id": 1,
            "host": True,
            "winner": False
        },
        {
            "id": 2,
            "name": "Player2",
            "turn": "SEGUNDO",
            "game_id": game_id,
            "game_state_id": 1,
            "host": False,
            "winner": False
        }
    ]
    
    player_repo.get_players_in_game.return_value = expected_players
    
    response = client.get(f"/players/{game_id}")
    
    assert response.status_code == 200
    assert response.json() == expected_players
    
    player_repo.get_players_in_game.assert_called_once_with(game_id, mock_db)
    
def test_get_player_by_id(player_repo, mock_db):
    game_id = 1
    player_id = 1
    expected_player = {
            "id": player_id,
            "name": "Player1",
            "turn": "PRIMERO",
            "game_id": game_id,
            "game_state_id": 1,
            "host": True,
            "winner": False
        }
    
    player_repo.get_player_by_id.return_value = expected_player
    response = client.get(f"/players/{game_id}/{player_id}")
    
    assert response.status_code == 200
    assert response.json() == expected_player
    
    player_repo.get_player_by_id.assert_called_once_with(game_id, player_id, mock_db)

def test_leave_game(player_repo, mock_game_logic, mock_db):
    
    game_id = 1
    player_id = 1
    
    player_repo.leave_game.return_value = {
        "message": "Player has successfully left the game",
        "changed_turn": True
    } 
    
    with client.websocket_connect("/ws") as websocket:
        response = client.post(
            f"/players/{player_id}/leave?game_id={game_id}"
        )
        print(player_repo.leave_game.return_value)
        print("Response status code:", response.status_code)
        print("Response JSON:", response.json())

        assert response.status_code == 200
        assert response.json() == {"type": "GAMES_LIST_UPDATE"}
        
        #Recibimos tres mensajes por broadcast
        #Guardamos en messages
        messages = []
        for _ in range(3):
            message = websocket.receive_json()
            messages.append(message)
        
        expected_messages = [
            {"type":f"{game_id}:GAME_INFO_UPDATE"},
            {"type": "GAMES_LIST_UPDATE"},
            {"type": f"{game_id}:GAME_INFO_UPDATE"}
        ]
        
        #Nos aseguramos que cada mensaje fue recibido
        for expected_message in expected_messages:
            assert expected_message in messages
        
        player_repo.leave_game.assert_called_once_with(game_id, player_id, mock_game_logic, mock_db)


def test_join_game(mock_game_logic, player_repo, game_repo ,mock_db):
    
    game_id = 1
    player_name = "player1"

    game_repo.count_players_in_game.return_value = 2

    
    game_repo.get_game_by_id.return_value = {"id": game_id, "name": "my game", "max_players": 3, "min_players": 3}
    player_repo.create_player.return_value = {"player_id": 5}
    
    with client.websocket_connect("/ws") as websocket:
        response = client.post(
            f"/players/join/{game_id}",
            json={"player_name": player_name}
        )
                
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {"player_id": 5}
        
        messages = []
        for _ in range(2):
            message = websocket.receive_json()
            messages.append(message)
        
        expected_messages = [
            {"type": f"{game_id}:GAME_INFO_UPDATE"},
            {"type": "GAMES_LIST_UPDATE"}
        ]
        
        #Nos aseguramos que cada mensaje fue recibido
        for expected_message in expected_messages:
            assert expected_message in messages
            
        game_repo.get_game_by_id.assert_called_once_with(game_id, mock_db)
        game_repo.count_players_in_game.assert_called_once_with(game_id, mock_db)
        player_repo.create_player.assert_called_once_with(game_id, player_name, mock_db)
    
    
    
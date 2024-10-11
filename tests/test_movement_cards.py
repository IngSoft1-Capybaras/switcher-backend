import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, Depends
from main import app

from movementCards.schemas import MovementCardSchema, typeEnum
from movementCards.movement_cards_repository import MovementCardsRepository
from movementCards.movement_cards_logic import MovementCardLogic, get_mov_cards_logic

from partial_movement.partial_movement_repository import PartialMovementRepository
from board.board_repository import BoardRepository
from board.schemas import BoardPosition

from database.db import get_db


client = TestClient(app)


# Mock DB session
@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


# Mock repository
@pytest.fixture
def mock_repo():
    return MagicMock(spec=MovementCardsRepository)

@pytest.fixture
def mock_mov_card_logic():
    return MagicMock(spec=MovementCardLogic)

@pytest.fixture
def mock_partial_mov_repo():
    return MagicMock(spec=PartialMovementRepository)

@pytest.fixture
def mock_board_repo():
    return MagicMock(spec=BoardRepository)


# Apply the override before running the tests
@pytest.fixture(autouse=True)
def setup_dependency_override(mock_repo,mock_mov_card_logic, mock_partial_mov_repo, mock_board_repo, mock_db):
    def override_get_db():
        return mock_db
    
    def override_get_mov_cards_logic():
        return mock_mov_card_logic
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_mov_cards_logic] = override_get_mov_cards_logic

    app.dependency_overrides[MovementCardsRepository] = lambda: mock_repo
    app.dependency_overrides[PartialMovementRepository] = lambda: mock_partial_mov_repo
    app.dependency_overrides[BoardRepository] = lambda: mock_board_repo
    yield
    app.dependency_overrides = {}  # Clean up overrides after test


def test_get_movement_cards_success(mock_repo, mock_db):
    mock_movement_cards = [
        MovementCardSchema(id=1, type=typeEnum.DIAGONAL_CONT, description="test", used=True, player_id=1, game_id=1), 
        MovementCardSchema(id=2, type=typeEnum.EN_L_DER, description="test", used=False, player_id=1, game_id=1)
    ]
    mock_repo.get_movement_cards.return_value = mock_movement_cards

    response = client.get("/deck/movement/1/1")

    assert response.status_code == 200
    assert response.json() == [card.model_dump() for card in mock_movement_cards]
    mock_repo.get_movement_cards.assert_called_once_with(1, 1, mock_db)


def test_get_movement_cards_not_found(mock_repo, mock_db):
    mock_repo.get_movement_cards.side_effect = HTTPException(
        status_code=404, 
        detail="There are no movement cards associated with this game and player"
    )

    response = client.get("/deck/movement/1/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "There are no movement cards associated with this game and player"}
    mock_repo.get_movement_cards.assert_called_once_with(1, 1, mock_db)


def test_get_movement_card_by_id_success(mock_repo, mock_db):
    mock_movement_card = MovementCardSchema(
        id=1, type=typeEnum.DIAGONAL_CONT, description="test", used=True, player_id=1, game_id=1
    )
    mock_repo.get_movement_card_by_id.return_value = mock_movement_card

    response = client.get("/deck/movement/1/1/1")

    assert response.status_code == 200
    assert response.json() == mock_movement_card.model_dump()
    mock_repo.get_movement_card_by_id.assert_called_once_with(1, 1, 1, mock_db)


def test_get_movement_card_by_id_not_found(mock_repo, mock_db):
    mock_repo.get_movement_card_by_id.side_effect = HTTPException(
        status_code=404, 
        detail="Movement card not found"
    )

    response = client.get("/deck/movement/1/1/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Movement card not found"}
    mock_repo.get_movement_card_by_id.assert_called_once_with(1, 1, 1, mock_db)


def test_play_movement_card(mock_repo,mock_mov_card_logic, mock_partial_mov_repo, mock_board_repo, mock_db):
    game_id = 1
    card_id = 1 
    player_id = 4
    pos_from = BoardPosition(pos=(0, 5)) 
    pos_to = BoardPosition(pos=(0, 3))
    
    mock_mov_card_logic.validate_movement.return_value = True
    
    mock_partial_mov_repo.create_partial_movement.return_value = None
    
    mock_repo.mark_card_partially_used.return_value = None
    
    mock_board_repo.switch_boxes.return_value = None
    
    with client.websocket_connect("/ws") as websocket:

        response = client.post(
            f"/deck/movement/play_card?game_id={game_id}&card_id={card_id}&player_id={player_id}",
            json={
                "pos_from": {"pos": [0, 5]},
                "pos_to": {"pos": [0, 3]}
            }
        )
        print(response.json())

        assert response.status_code == 201
        assert response.json() == {"message": "Great move..."}
        
        game_state_update = websocket.receive_json()
        assert game_state_update["type"] == f"{game_id}: MOVEMENT_UPDATE"
        
        mock_mov_card_logic.validate_movement.assert_called_once_with(card_id,pos_from, pos_to)
        mock_partial_mov_repo.create_partial_movement.assert_called_once_with(game_id, player_id, card_id, pos_from, pos_to, mock_db)
        mock_repo.mark_card_partially_used.assert_called_once_with(card_id, mock_db)
        mock_board_repo.switch_boxes.assert_called_once_with(game_id, pos_from, pos_to, mock_db)
        
def test_play_movement_card_invalid_position():
    game_id = 1
    card_id = 1 
    player_id = 4
    
    response = client.post(
        f"/deck/movement/play_card?game_id={game_id}&card_id={card_id}&player_id={player_id}",
        json={
            "pos_from": {"pos": [0, 5]},
            "pos_to": {"pos": [2, 7]}
        }
    )
    
    assert response.status_code == 422  # Error de validacion de tipo
    assert response.json()["detail"][0]["type"] == "less_than_equal"
    assert response.json()["detail"][0]["msg"] == "Input should be less than or equal to 5"

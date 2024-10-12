import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, Depends
from movementCards.schemas import MovementCardSchema, typeEnum
from main import app
from movementCards.movement_cards_repository import MovementCardsRepository
from partial_movement.partial_movement_repository import PartialMovementRepository, get_partial_movement_repository
from partial_movement.schemas import PartialMovementsBase
from board.board_repository import BoardRepository
from board.schemas import BoardPosition
from database.db import get_db
from connection_manager import manager


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
def mock_partial_movement_repo():
    return MagicMock(spec=PartialMovementRepository)

@pytest.fixture
def mock_board_repo():
    return MagicMock(spec=BoardRepository)


# Apply the override before running the tests
@pytest.fixture(autouse=True)
def setup_dependency_override(mock_repo, mock_db, mock_partial_movement_repo, mock_board_repo):
    def override_get_db():
        return mock_db
    
    def override_get_partial_movement_repository():
        return mock_partial_movement_repo
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[MovementCardsRepository] = lambda: mock_repo
    app.dependency_overrides[PartialMovementRepository] = lambda: mock_partial_movement_repo
    app.dependency_overrides[get_partial_movement_repository] = override_get_partial_movement_repository

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


def test_undo_movement_success(mock_partial_movement_repo, mock_board_repo, mock_repo, mock_db):
    # Mockeo un ultimo movimiento
    mock_last_movement = MagicMock()
    mock_last_movement.pos_from_x = 1
    mock_last_movement.pos_from_y = 1
    mock_last_movement.pos_to_x = 2
    mock_last_movement.pos_to_y = 2
    mock_last_movement.mov_card_id = 7
    
    game_id = 1
    player_id = 1
    
    pos_from = BoardPosition(pos=(1, 1))
    pos_to = BoardPosition(pos=(2, 2))

    
    mock_partial_movement_repo.undo_movement.return_value = mock_last_movement
    with client.websocket_connect("/ws") as websocket:
        response = client.post(f"/deck/movement/undo_move?game_id={game_id}&player_id={player_id}")

        assert response.status_code == 200
        assert response.json() == {"message": "The movement was undone successfully"}
        
        # Verifico que los metodos usados se llamen
        mock_partial_movement_repo.undo_movement.assert_called_once_with(mock_db)
        mock_board_repo.switch_boxes.assert_called_once_with(
            game_id, pos_from,pos_to, mock_db
        )
        mock_repo.mark_card_in_player_hand( mock_last_movement.mov_card_id, mock_db)
        
        # Verifico que se haya mandado el mensaje po ws
        movement_update = websocket.receive_json()
        assert movement_update["type"] == f"MOVEMENT_UPDATE"


def test_undo_movement_no_last_move(mock_partial_movement_repo, mock_board_repo, mock_db):
    mock_partial_movement_repo.undo_movement.side_effect = HTTPException(
        status_code=404,
        detail="There is no partial movement to undo"
    )

    response = client.post("/deck/movement/undo_move?game_id=1&player_id=1")

    assert response.status_code == 404
    assert response.json() == {"detail": "There is no partial movement to undo"}
    mock_partial_movement_repo.undo_movement.assert_called_once_with(mock_db)

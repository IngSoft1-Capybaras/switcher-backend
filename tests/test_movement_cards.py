import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, Depends
from movementCards.schemas import MovementCardSchema, typeEnum
from main import app
from movementCards.movement_cards_repository import MovementCardsRepository
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


# Apply the override before running the tests
@pytest.fixture(autouse=True)
def setup_dependency_override(mock_repo, mock_db):
    def override_get_db():
        return mock_db
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[MovementCardsRepository] = lambda: mock_repo
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

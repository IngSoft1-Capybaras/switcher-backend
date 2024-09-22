import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from .endpoints import movement_cards_router
from .movement_cards_repository import MovementCardsRepository
from .schemas import MovementCardSchema
from main import app

app.include_router(movement_cards_router)

client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db():
    return MagicMock()


# Mock repository
@pytest.fixture
def mock_repo():
    return MagicMock(spec=MovementCardsRepository)


@patch('.movement_cards_repository.MovementCardsRepository')
def test_get_movement_cards_success(mock_db, mock_repo):

    mock_movement_cards = [MovementCardSchema(id=1, player_id=1), MovementCardSchema(id=2, player_id=1)]
    mock_repo.get_movement_cards.return_value = mock_movement_cards

    response = client.get("/deck/movement/1/1")

    assert response.status_code == 200
    assert response.json() == [card.dict() for card in mock_movement_cards]
    mock_repo.get_movement_cards.assert_called_once_with(1, 1, mock_db)


@patch('.movement_cards_repository.MovementCardsRepository')
def test_get_movement_cards_not_found(mock_db, mock_repo):
    mock_repo.get_movement_cards.side_effect = HTTPException(status_code=404, 
                                                             detail="There no movement cards associated with this game and player")

    response = client.get("/deck/movement/1/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "There no movement cards associated with this game and player"}
    mock_repo.get_movement_cards.assert_called_once_with(1, 1, mock_db)


@patch('.movement_cards_repository.MovementCardsRepository')
def test_get_movement_card_by_id_success(mock_db, mock_repo):
    mock_movement_card = MovementCardSchema(id=1, player_id=1)
    mock_repo.get_movement_card_by_id.return_value = mock_movement_card

    response = client.get("/deck/movement/1/1/1")

    assert response.status_code == 200
    assert response.json() == mock_movement_card.dict()
    mock_repo.get_movement_card_by_id.assert_called_once_with(1, 1, 1, mock_db)


@patch('.movement_cards_repository.MovementCardsRepository')
def test_get_movement_card_by_id_not_found(mock_db, mock_repo):
    mock_repo.get_movement_card_by_id.side_effect = HTTPException(status_code=404, detail="Movement card not found")

    response = client.get("/deck/movement/1/1/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Movement card not found"}
    mock_repo.get_movement_card_by_id.assert_called_once_with(1, 1, 1, mock_db)
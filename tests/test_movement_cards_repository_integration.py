import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from sqlalchemy.orm.exc import NoResultFound
from movementCards.movement_cards_repository import MovementCardsRepository
from movementCards.models import MovementCard
from movementCards.schemas import MovementCardSchema

# Mock database 
@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def movement_cards_repository():
    return MovementCardsRepository()


def test_get_movement_cards_success(mock_db, movement_cards_repository):

    mock_movement_cards = [
        MovementCard(id=1, player_id=1),
        MovementCard(id=2, player_id=1),
    ]
    mock_db.query().filter().filter().all.return_value = mock_movement_cards
    expected_result = [MovementCardSchema.from_orm(card) for card in mock_movement_cards]

    result = movement_cards_repository.get_movement_cards(game_id=1, player_id=1, db=mock_db)

    assert result == expected_result
    mock_db.query().filter().filter().all.assert_called_once()


def test_get_movement_cards_not_found(mock_db, movement_cards_repository):
    mock_db.query().filter().filter().all.return_value = []

    with pytest.raises(HTTPException) as exc_info:
        movement_cards_repository.get_movement_cards(game_id=1, player_id=1, db=mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "There no movement cards associated with this game and player"



def test_get_movement_card_by_id_success(mock_db, movement_cards_repository):
    mock_movement_card = MovementCard(id=1, player_id=1)
    mock_db.query().filter().filter().one.return_value = mock_movement_card
    expected_result = MovementCardSchema.from_orm(mock_movement_card)

    result = movement_cards_repository.get_movement_card_by_id(game_id=1, player_id=1, card_id=1, db=mock_db)

    assert result == expected_result
    mock_db.query().filter().filter().one.assert_called_once()


def test_get_movement_card_by_id_not_found(mock_db, movement_cards_repository):
    mock_db.query().filter().filter().one.side_effect = NoResultFound

    with pytest.raises(HTTPException) as exc_info:
        movement_cards_repository.get_movement_card_by_id(game_id=1, player_id=1, card_id=1, db=mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Movement card not found"
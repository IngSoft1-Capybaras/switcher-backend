import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from sqlalchemy.orm.exc import NoResultFound
from .figure_cards_repository import FigureCardsRepository
from .models import FigureCard
from .schemas import FigureCardSchema

# Mock database 
@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def figure_cards_repository():
    return FigureCardsRepository()



def test_get_figure_cards_success(mock_db, figure_cards_repository):

    mock_figure_cards = [
        FigureCard(id=1, player_id=1),
        FigureCard(id=2, player_id=1),
    ]
    mock_db.query().filter().filter().all.return_value = mock_figure_cards
    expected_result = [FigureCardSchema.from_orm(card) for card in mock_figure_cards]

    result = figure_cards_repository.get_figure_cards(game_id=1, player_id=1, db=mock_db)

    assert result == expected_result
    mock_db.query().filter().filter().all.assert_called_once()



def test_get_figure_cards_not_found(mock_db, figure_cards_repository):
    mock_db.query().filter().filter().all.return_value = []

    with pytest.raises(HTTPException) as exc_info:
        figure_cards_repository.get_figure_cards(game_id=1, player_id=1, db=mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "There no figure cards associated with this game and player"



def test_get_figure_card_by_id_success(mock_db, figure_cards_repository):
    mock_figure_card = FigureCard(id=1, player_id=1)
    mock_db.query().filter().filter().one.return_value = mock_figure_card
    expected_result = FigureCardSchema.from_orm(mock_figure_card)

    result = figure_cards_repository.get_figure_card_by_id(game_id=1, player_id=1, card_id=1, db=mock_db)

    assert result == expected_result
    mock_db.query().filter().filter().one.assert_called_once()


def test_get_figure_card_by_id_not_found(mock_db, figure_cards_repository):
    mock_db.query().filter().filter().one.side_effect = NoResultFound

    with pytest.raises(HTTPException) as exc_info:
        figure_cards_repository.get_figure_card_by_id(game_id=1, player_id=1, card_id=1, db=mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Figure card not found"

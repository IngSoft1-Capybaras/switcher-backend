import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from .endpoints import figure_cards_router
from .figure_cards_repository import FigureCardsRepository
from .schemas import FigureCardSchema
from main import app

app.include_router(figure_cards_router)

client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db():
    return MagicMock()


# Mock repository
@pytest.fixture
def mock_repo():
    return MagicMock(spec=FigureCardsRepository)


@patch('.figure_cards_repository.FigureCardsRepository')
def test_get_figure_cards_success(mock_db, mock_repo):

    mock_figure_cards = [FigureCardSchema(id=1, player_id=1), FigureCardSchema(id=2, player_id=1)]
    mock_repo.get_figure_cards.return_value = mock_figure_cards

    response = client.get("/deck/figure/1/1")

    assert response.status_code == 200
    assert response.json() == [card.dict() for card in mock_figure_cards]
    mock_repo.get_figure_cards.assert_called_once_with(1, 1, mock_db)


@patch('.figure_cards_repository.FigureCardsRepository')
def test_get_figure_cards_not_found(mock_db, mock_repo):
    mock_repo.get_figure_cards.side_effect = HTTPException(status_code=404, detail="There no figure cards associated with this game and player")

    response = client.get("/deck/figure/1/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "There no figure cards associated with this game and player"}
    mock_repo.get_figure_cards.assert_called_once_with(1, 1, mock_db)


@patch('.figure_cards_repository.FigureCardsRepository')
def test_get_figure_card_by_id_success(mock_db, mock_repo):
    mock_figure_card = FigureCardSchema(id=1, player_id=1)
    mock_repo.get_figure_card_by_id.return_value = mock_figure_card

    response = client.get("/deck/figure/1/1/1")

    assert response.status_code == 200
    assert response.json() == mock_figure_card.dict()
    mock_repo.get_figure_card_by_id.assert_called_once_with(1, 1, 1, mock_db)


@patch('.figure_cards_repository.FigureCardsRepository')
def test_get_figure_card_by_id_not_found(mock_db, mock_repo):
    mock_repo.get_figure_card_by_id.side_effect = HTTPException(status_code=404, detail="Figure card not found")

    response = client.get("/deck/figure/1/1/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Figure card not found"}
    mock_repo.get_figure_card_by_id.assert_called_once_with(1, 1, 1, mock_db)

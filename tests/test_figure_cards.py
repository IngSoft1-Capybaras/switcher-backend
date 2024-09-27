import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from fastapi import HTTPException
from sqlalchemy.orm import Session
from figureCards.endpoints import figure_cards_router
from figureCards.figure_cards_repository import FigureCardsRepository
from figureCards.schemas import FigureCardSchema
from figureCards.models import typeEnum, DifficultyEnum
from database.db import get_db
from main import app

app.include_router(figure_cards_router)

client = TestClient(app)


# Mock database
@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


# Mock repository
@pytest.fixture
def mock_repo():
    return MagicMock(spec=FigureCardsRepository)


# Apply the override before running the tests
@pytest.fixture(autouse=True)
def setup_dependency_override(mock_repo, mock_db):
    def override_get_db():
        return mock_db
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[FigureCardsRepository] = lambda: mock_repo
    yield
    app.dependency_overrides = {}  # Clean up overrides after test


def test_get_figure_cards_success(mock_repo, mock_db):
    mock_figure_cards = [
        FigureCardSchema(id=1, type=typeEnum.TYPE_1, show=True, difficulty=DifficultyEnum.EASY, player_id=1, game_id=1),
        FigureCardSchema(id=2, type=typeEnum.TYPE_1, show=True, difficulty=DifficultyEnum.HARD, player_id=1, game_id=1)
    ]
    mock_repo.get_figure_cards.return_value = mock_figure_cards

    response = client.get("/deck/figure/1/1")
    
    assert response.status_code == 200
    assert response.json() == [card.model_dump() for card in mock_figure_cards]
    mock_repo.get_figure_cards.assert_called_once_with(1, 1, mock_db)


def test_get_figure_cards_not_found(mock_repo, mock_db):
    mock_repo.get_figure_cards.side_effect = HTTPException(
        status_code=404, 
        detail="There no figure cards associated with this game and player"
    )

    response = client.get("/deck/figure/1/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "There no figure cards associated with this game and player"}
    mock_repo.get_figure_cards.assert_called_once_with(1, 1, mock_db)


def test_get_figure_card_by_id_success(mock_repo, mock_db):
    mock_figure_card = FigureCardSchema(
        id=1, type=typeEnum.TYPE_1, show=True, difficulty=DifficultyEnum.EASY , player_id=1, game_id=1)
    mock_repo.get_figure_card_by_id.return_value = mock_figure_card

    response = client.get("/deck/figure/1/1/1")

    assert response.status_code == 200
    assert response.json() == mock_figure_card.model_dump()
    mock_repo.get_figure_card_by_id.assert_called_once_with(1, 1, 1, mock_db)


def test_get_figure_card_by_id_not_found(mock_repo, mock_db):
    mock_repo.get_figure_card_by_id.side_effect = HTTPException(status_code=404, detail="Figure card not found")

    response = client.get("/deck/figure/1/1/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Figure card not found"}
    mock_repo.get_figure_card_by_id.assert_called_once_with(1, 1, 1, mock_db)

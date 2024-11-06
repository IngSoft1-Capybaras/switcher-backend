import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock
from fastapi import HTTPException
from sqlalchemy.orm import Session

from figureCards.figure_cards_repository import FigureCardsRepository
from figureCards.schemas import FigureCardSchema, PlayFigureCardInput
from figureCards.models import typeEnum, DifficultyEnum
from figureCards.figure_cards_logic import FigureCardsLogic, get_fig_cards_logic

from board.schemas import ColorEnum, BoxIn

from database.db import get_db
from main import app

client = TestClient(app)


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_repo():
    return MagicMock(spec=FigureCardsRepository)

@pytest.fixture
def mock_fig_cards_logic():
    return MagicMock(spec=FigureCardsLogic)

# Apply the override before running the tests
@pytest.fixture(autouse=True)
def setup_dependency_override(mock_fig_cards_logic, mock_repo, mock_db):
    def override_get_db():
        return mock_db
    
    def override_get_fig_cards_logic():
        return mock_fig_cards_logic
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[FigureCardsRepository] = lambda: mock_repo
    app.dependency_overrides[get_fig_cards_logic] = override_get_fig_cards_logic

    yield
    app.dependency_overrides = {}  # Clean up overrides after test


def test_get_figure_cards_success(mock_repo, mock_db):
    mock_figure_cards = [

        FigureCardSchema(id=1, type=typeEnum.FIG01, show=True, difficulty=DifficultyEnum.EASY, player_id=1, game_id=1, blocked = False),
        FigureCardSchema(id=2, type=typeEnum.FIG01, show=True, difficulty=DifficultyEnum.HARD, player_id=1, game_id=1, blocked = False)

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
        id=1, type=typeEnum.FIG01, show=True, difficulty=DifficultyEnum.EASY , player_id=1, game_id=1, blocked = False)
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

@pytest.mark.asyncio
async def test_play_figure_card(mock_fig_cards_logic, mock_db):
    figureInfo = PlayFigureCardInput(
        game_id=1,
        player_id=1,
        card_id=1,
        figure=[ BoxIn(pos_x = 0,  pos_y = 0, color = ColorEnum.RED)]
    )

    mock_fig_cards_logic.play_figure_card = AsyncMock(return_value={"message": "Figure card played"})

    response = client.post("/deck/figure/play_card", json=figureInfo.model_dump())

    assert response.status_code == 200


def test_block_figure_card(mock_repo, mock_db):
    game_id = 1
    figure_card_id = 1
    
    mock_repo.block_figure_card.return_value = {"message": "The figure cards was successfully blocked"}

    with client.websocket_connect("/ws") as websocket:
        response = client.post(
            f"/deck/figure/{game_id}/{figure_card_id}/block_card/"
        )

        assert response.status_code == 201
        assert response.json() == {"message": "The figure cards was successfully blocked"}

        block_card = websocket.receive_json()
        assert block_card["type"] == f"{game_id}:BLOCK_CARD"

        mock_repo.block_figure_card.assert_called_once_with(game_id, figure_card_id, mock_db)
        
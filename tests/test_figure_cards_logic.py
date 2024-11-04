import pytest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from figureCards.figure_cards_logic import FigureCardsLogic
from figureCards.models import typeEnum, DirectionEnum

from player.player_logic import PlayerLogic

from board.schemas import ColorEnum, BoxOut, BoardAndBoxesOut

from gameState.schemas import GameStateInDB, StateEnum
from fastapi import HTTPException

@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def player_repo():
    return MagicMock()

@pytest.fixture
def game_repo():
    return MagicMock()

@pytest.fixture
def game_state_repo():
    return MagicMock()

@pytest.fixture
def board_repo():
    return MagicMock()

@pytest.fixture
def fig_card_repo():
    return MagicMock()

@pytest.fixture
def fig_cards_logic(player_repo, fig_card_repo, game_repo, game_state_repo, board_repo):
    return FigureCardsLogic(player_repo=player_repo ,fig_card_repo=fig_card_repo, game_repo=game_repo, game_state_repo=game_state_repo, board_repo=board_repo)

@pytest.fixture
def player_logic(player_repo):
    return PlayerLogic(player_repo= player_repo)

def test_create_fig_deck(fig_cards_logic, player_logic):
    mock_session = MagicMock()
    game_id = 1
    
    mock_player_1 = MagicMock(id=1)
    
    player_logic.player_repo.get_players_in_game.return_value = [mock_player_1]
    
    with patch('random.shuffle', lambda x: x):
        response = fig_cards_logic.create_fig_deck(mock_session, game_id)
    
    assert response == {"message": "Figure deck created"}
    
    expected_calls = [
        ((1, game_id, typeEnum.FIGE01, False, mock_session),),
        ((1, game_id, typeEnum.FIGE02, False, mock_session),),
        ((1, game_id, typeEnum.FIGE03, False, mock_session),),
        ((1, game_id, typeEnum.FIGE04, False, mock_session),),
        ((1, game_id, typeEnum.FIGE05, False, mock_session),),
        ((1, game_id, typeEnum.FIGE06, False, mock_session),),
        ((1, game_id, typeEnum.FIGE07, False, mock_session),),
        ((1, game_id, typeEnum.FIG01, True, mock_session),),
        ((1, game_id, typeEnum.FIG02, True, mock_session),),
        ((1, game_id, typeEnum.FIG03, True, mock_session),),
        ((1, game_id, typeEnum.FIG04, False, mock_session),),
        ((1, game_id, typeEnum.FIG05, False, mock_session),),
        ((1, game_id, typeEnum.FIG06, False, mock_session),),
        ((1, game_id, typeEnum.FIG07, False, mock_session),),
        ((1, game_id, typeEnum.FIG08, False, mock_session),),
        ((1, game_id, typeEnum.FIG09, False, mock_session),),
        ((1, game_id, typeEnum.FIG10, False, mock_session),),
        ((1, game_id, typeEnum.FIG11, False, mock_session),),
        ((1, game_id, typeEnum.FIG12, False, mock_session),),
        ((1, game_id, typeEnum.FIG13, False, mock_session),),
        ((1, game_id, typeEnum.FIG14, False, mock_session),),
        ((1, game_id, typeEnum.FIG15, False, mock_session),),
        ((1, game_id, typeEnum.FIG16, False, mock_session),),
        ((1, game_id, typeEnum.FIG17, False, mock_session),),
        ((1, game_id, typeEnum.FIG18, False, mock_session),)
    ]
    
    # fig_cards_logic.fig_card_repo.create_figure_card.assert_has_calls(expected_calls, any_order=True)
    # me fijo que tenga 25 llamadas
    assert fig_cards_logic.fig_card_repo.create_figure_card.call_count == len(expected_calls)
    
    calls = fig_cards_logic.fig_card_repo.create_figure_card.call_args_list
    
    # me fijo que solo hayan 3 cartas mostradas
    shown_cards = sum(1 for call in calls if call[0][3] is True)
    assert shown_cards == 3

    # me fijo que las funciones se llamen correctamente
    for call in calls:
        assert len(call[0]) == 5 # cada llamada tiene 5 arguments
        assert isinstance(call[0][0], int)
        assert isinstance(call[0][1], int)
        assert isinstance(call[0][2], typeEnum)
        assert isinstance(call[0][3], bool)


def test_create_fig_deck_no_players(fig_cards_logic, player_logic):
    mock_session = MagicMock()
    game_id = 1
        
    player_logic.player_repo.get_players_in_game.return_value = []
    
    with patch('random.shuffle', lambda x: x):
        response = fig_cards_logic.create_fig_deck(mock_session, game_id)
    
    assert response == {"message": "Figure deck was not created, there no players in game"}
    

def test_is_pointer_different_from_formed_figures(fig_cards_logic):
    pointer = (2, 3)
    
    figures = [
        [
            BoxOut(id=1, color=ColorEnum.RED, pos_x=0, pos_y=0, highlighted=False, figure_id=1, figure_type=typeEnum.FIG01),
            BoxOut(id=2, color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIG01)
        ],
        [
            BoxOut(id=3, color=ColorEnum.BLUE, pos_x=2, pos_y=3, highlighted=False, figure_id=2, figure_type=typeEnum.FIG02),
            BoxOut(id=4, color=ColorEnum.BLUE, pos_x=3, pos_y=3, highlighted=False, figure_id=2, figure_type=typeEnum.FIG02)
        ]
    ]
    
    result = fig_cards_logic.is_pointer_different_from_formed_figures(pointer, figures)
    assert result == False

    pointer = (4, 4)
    result = fig_cards_logic.is_pointer_different_from_formed_figures(pointer, figures)
    assert result == pointer
    

def test_check_surroundings_invalid_pointer(fig_cards_logic):
    path = []
    figure = [{"pos_x": 1, "pos_y": 1, "color": ColorEnum.RED}]
    pointer = (1, 1)
    board = BoardAndBoxesOut(
        game_id=1,
        board_id=1,
        boxes=[
            [BoxOut(id=1, color=ColorEnum.BLUE, pos_x=0, pos_y=0, highlighted=False)],
            [BoxOut(id=2, color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False)],
            [BoxOut(id=3, color=ColorEnum.BLUE, pos_x=2, pos_y=2, highlighted=False)]
        ],
        figures = []
    )
    color = ColorEnum.RED
    mock_db = MagicMock()

    fig_cards_logic.move_pointer = MagicMock(side_effect=lambda pointer, direction: (pointer[0] + 1, pointer[1]) if direction == DirectionEnum.RIGHT else (pointer[0] - 1, pointer[1]) if direction == DirectionEnum.LEFT else (pointer[0], pointer[1] + 1) if direction == DirectionEnum.DOWN else (pointer[0], pointer[1] - 1))
    fig_cards_logic.is_valid_pointer = MagicMock(side_effect=lambda pointer: False)
    fig_cards_logic.belongs_to_figure = MagicMock(side_effect=lambda pointer, figure: any(box["pos_x"] == pointer[0] and box["pos_y"] == pointer[1] for box in figure))

    result = fig_cards_logic.check_surroundings(path, figure, pointer, board, color, mock_db)
    assert result == True


def test_is_valid_pointer(fig_cards_logic):
    pointer_inside_bounds = (3, 4)
    pointer_outside_bounds = (6, 7)
    pointer_negative = (-1, 2)

    assert fig_cards_logic.is_valid_pointer(pointer_inside_bounds) == True

    assert fig_cards_logic.is_valid_pointer(pointer_outside_bounds) == False

    assert fig_cards_logic.is_valid_pointer(pointer_negative) == False
    
def test_move_pointer(fig_cards_logic):
    initial_pointer = (2, 2)

    result = fig_cards_logic.move_pointer(initial_pointer, DirectionEnum.UP)
    assert result == (2, 1)

    result = fig_cards_logic.move_pointer(initial_pointer, DirectionEnum.DOWN)
    assert result == (2, 3)

    result = fig_cards_logic.move_pointer(initial_pointer, DirectionEnum.LEFT)
    assert result == (1, 2)

    result = fig_cards_logic.move_pointer(initial_pointer, DirectionEnum.RIGHT)
    assert result == (3, 2)
    


def test_belongs_to_figure(fig_cards_logic):
    figure = [
        BoxOut(id=1, color="RED", pos_x=1, pos_y=1, highlighted=False, figure_id=1, figure_type="FIG01"),
        BoxOut(id=2, color="BLUE", pos_x=2, pos_y=2, highlighted=False, figure_id=1, figure_type="FIG01")
    ]
    
    pointer_inside = (1, 1)
    pointer_outside = (3, 3)

    assert fig_cards_logic.belongs_to_figure(pointer_inside, figure) == True

    assert fig_cards_logic.belongs_to_figure(pointer_outside, figure) == False


def test_get_pointer_from_figure(fig_cards_logic):
    figure = [
        BoxOut(id=1, color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIG01),
        BoxOut(id=2, color=ColorEnum.BLUE, pos_x=1, pos_y=2, highlighted=False, figure_id=1, figure_type=typeEnum.FIG01),
        BoxOut(id=3, color=ColorEnum.RED, pos_x=1, pos_y=3, highlighted=False, figure_id=1, figure_type=typeEnum.FIG01)
    ]

    result = fig_cards_logic.get_pointer_from_figure(figure, 0)
    assert result == (1, 1)

    result = fig_cards_logic.get_pointer_from_figure(figure, 1)
    assert result == (1, 3)

    result = fig_cards_logic.get_pointer_from_figure(figure, 2)
    assert result == (1, 3)

    result = fig_cards_logic.get_pointer_from_figure(figure, 3)
    assert result == (1, 1)
    
def test_get_pointer_from_figure_empty_figure(fig_cards_logic):
    figure = []

    with pytest.raises(HTTPException) as exc_info:
        fig_cards_logic.get_pointer_from_figure(figure, 0)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Empty figure"
    

def test_get_pointer_from_figure_invalid_rotation(fig_cards_logic):
    figure = [
        BoxOut(id=1, color=ColorEnum.RED, pos_x=1, pos_y=1, highlighted=False, figure_id=1, figure_type=typeEnum.FIG01)
    ]

    with pytest.raises(HTTPException) as exc_info:
        fig_cards_logic.get_pointer_from_figure(figure, 4)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Invalid rotation"
    
def test_get_board_or_404_board_found(fig_cards_logic):
    game_id = 1
    mock_db = MagicMock()

    mock_board = {
        "game_id":game_id,
        "board_id":1,
        "boxes":[]
    }
    
    fig_cards_logic.board_repo.get_configured_board.return_value = mock_board
    
    result = fig_cards_logic.get_board_or_404(game_id, mock_db)

    print(result)
    assert result == mock_board
    

def test_check_game_in_progress_game_not_found(fig_cards_logic):
    game_id = 1
    mock_db = MagicMock()

    fig_cards_logic.game_state_repo.get_game_state_by_id.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        fig_cards_logic.check_game_in_progress(game_id, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Game not found when getting formed figures"

def test_check_game_in_progress_game_not_in_progress(fig_cards_logic):
    game_id = 1
    mock_db = MagicMock()

    mock_game_state = GameStateInDB(
        id=1,
        state=StateEnum.FINISHED,
        game_id=game_id,
        current_player=None
    )
    fig_cards_logic.game_state_repo.get_game_state_by_id.return_value = mock_game_state
    with pytest.raises(HTTPException) as exc_info:
        fig_cards_logic.check_game_in_progress(game_id, mock_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Game not in progress when getting formed figures"

def test_check_game_in_progress_game_playing(fig_cards_logic):
    game_id = 1
    mock_db = MagicMock()

    mock_game_state = GameStateInDB(
        id=1,
        state=StateEnum.PLAYING,
        game_id=game_id,
        current_player=None
    )
    fig_cards_logic.game_state_repo.get_game_state_by_id.return_value = mock_game_state
    result = fig_cards_logic.check_game_in_progress(game_id, mock_db)

    assert result is None
import pytest
from unittest.mock import MagicMock, patch
from figureCards.utils import FigureCardUtils
from figureCards.models import typeEnum
from player.player_logic import PlayerLogic

@pytest.fixture
def player_repo():
    return MagicMock()

@pytest.fixture
def fig_cards_utils(player_repo):
    mock_fig_cards_repo = MagicMock()
    return FigureCardUtils(player_repo=player_repo ,fig_card_repo=mock_fig_cards_repo)

@pytest.fixture
def player_logic(player_repo):
    return PlayerLogic(player_repo= player_repo)

def test_create_fig_deck(fig_cards_utils, player_logic):
    mock_session = MagicMock()
    game_id = 1
    
    mock_player_1 = MagicMock(id=1)
    
    player_logic.player_repo.get_players_in_game.return_value = [mock_player_1]
    
    with patch('random.shuffle', lambda x: x):
        response = fig_cards_utils.create_fig_deck(mock_session, game_id)
    
    assert response == {"message": "Figure deck created"}
    
    expected_calls = [
        ((1, game_id, typeEnum.TYPE_4, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_4, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_4, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_5, True, mock_session),),
        ((1, game_id, typeEnum.TYPE_5, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_5, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_5, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_6, True, mock_session),),
        ((1, game_id, typeEnum.TYPE_6, True, mock_session),),
        ((1, game_id, typeEnum.TYPE_6, True, mock_session),),
        ((1, game_id, typeEnum.TYPE_1, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_1, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_1, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_1, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_1, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_2, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_2, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_2, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_2, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_3, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_3, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_3, False, mock_session),),
        ((1, game_id, typeEnum.TYPE_3, False, mock_session),)
    ]
    
    # fig_cards_utils.fig_card_repo.create_figure_card.assert_has_calls(expected_calls, any_order=True)
    # me fijo que tenga 23 llamadas
    assert fig_cards_utils.fig_card_repo.create_figure_card.call_count == len(expected_calls)
    
    calls = fig_cards_utils.fig_card_repo.create_figure_card.call_args_list
    
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
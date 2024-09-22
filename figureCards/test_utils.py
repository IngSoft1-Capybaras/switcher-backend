import pytest
from unittest.mock import MagicMock, patch
from .utils import FigureCardUtils
from .models import typeEnum
from player.utils import PlayerUtils

@pytest.fixture
def player_repo():
    return MagicMock()

@pytest.fixture
def fig_cards_utils(player_repo):
    mock_fig_cards_repo = MagicMock()
    return FigureCardUtils(player_repo=player_repo ,fig_card_repo=mock_fig_cards_repo)

@pytest.fixture
def player_utils(player_repo):
    return PlayerUtils(player_repo= player_repo)

def test_create_fig_deck(fig_cards_utils, player_utils):
    mock_session = MagicMock()
    game_id = 1
    
    mock_player_1 = MagicMock(id=1)
    
    player_utils.player_repo.get_players_in_game.return_value = [mock_player_1]
    
    with patch('random.shuffle', lambda x: x):
        response = fig_cards_utils.create_fig_deck(mock_session, game_id)
    
    assert response == {"message": "Figure deck created"}
    
    expected_calls = [
        ((1, game_id, typeEnum.TYPE_4, mock_session),),
        ((1, game_id, typeEnum.TYPE_4, mock_session),),
        ((1, game_id, typeEnum.TYPE_4, mock_session),),
        ((1, game_id, typeEnum.TYPE_5, mock_session),),
        ((1, game_id, typeEnum.TYPE_5, mock_session),),
        ((1, game_id, typeEnum.TYPE_5, mock_session),),
        ((1, game_id, typeEnum.TYPE_5, mock_session),),
        ((1, game_id, typeEnum.TYPE_6, mock_session),),
        ((1, game_id, typeEnum.TYPE_6, mock_session),),
        ((1, game_id, typeEnum.TYPE_6, mock_session),),
        ((1, game_id, typeEnum.TYPE_1, mock_session),),
        ((1, game_id, typeEnum.TYPE_1, mock_session),),
        ((1, game_id, typeEnum.TYPE_1, mock_session),),
        ((1, game_id, typeEnum.TYPE_1, mock_session),),
        ((1, game_id, typeEnum.TYPE_1, mock_session),),
        ((1, game_id, typeEnum.TYPE_2, mock_session),),
        ((1, game_id, typeEnum.TYPE_2, mock_session),),
        ((1, game_id, typeEnum.TYPE_2, mock_session),),
        ((1, game_id, typeEnum.TYPE_2, mock_session),),
        ((1, game_id, typeEnum.TYPE_3, mock_session),),
        ((1, game_id, typeEnum.TYPE_3, mock_session),),
        ((1, game_id, typeEnum.TYPE_3, mock_session),),
        ((1, game_id, typeEnum.TYPE_3, mock_session),)      
    ]
    
    fig_cards_utils.fig_card_repo.create_figure_card.assert_has_calls(expected_calls, any_order=True)
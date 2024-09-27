import pytest
from unittest.mock import MagicMock, patch
from player.utils import PlayerUtils
from player.models import turnEnum


@pytest.fixture
def player_utils():
    mock_player_repo = MagicMock()
    return PlayerUtils(player_repo=mock_player_repo)

def test_assign_random_turns(player_utils):
    mock_session = MagicMock()
    
    mock_player_1 = MagicMock(id=1)
    mock_player_2 = MagicMock(id=2)
    
    
    players = [mock_player_1, mock_player_2]
    with patch('random.sample', return_value=[1,2]):
        first_player_id = player_utils.assign_random_turns(players, mock_session)
    
    assert first_player_id == 1
    player_utils.player_repo.assign_turn_player.assert_any_call(1, turnEnum.PRIMERO, mock_session)
    player_utils.player_repo.assign_turn_player.assert_any_call(2, turnEnum.SEGUNDO, mock_session)
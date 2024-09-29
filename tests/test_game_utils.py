from tkinter import N
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from game.utils import GameUtils
from player.models import Player

@pytest.fixture
def game_utils():
    mock_game_repo = MagicMock()
    return GameUtils(game_repository=mock_game_repo)

@pytest.mark.asyncio
async def test_check_win_condition(game_utils):
    game_id = 1
    game_state_id = 1
    #Mock game 
    mock_game = MagicMock()
    mock_game.id = game_id
    mock_game.players = [Player(id=1, name="Player1", game_id = game_id , game_state_id = game_state_id, host=True, winner = False)]
    
    #Mock session
    mock_session = MagicMock()
    
    #Mock handle win
    with patch.object(game_utils, 'handle_win', return_value = None) as mock_handle_win:
        result = await game_utils.check_win_condition(mock_game, mock_session)
    
        mock_handle_win.assert_called_once_with(mock_game.id, mock_game.players[0] ,mock_session)
        assert result
    

    
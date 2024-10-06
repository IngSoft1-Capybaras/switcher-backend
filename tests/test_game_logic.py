import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from game.game_logic import GameLogic
from gameState.models import StateEnum
from player.models import Player

@pytest.fixture
def game_logic():
    mock_game_repo = MagicMock()
    mock_game_state_repo = MagicMock()
    mock_player_repo = MagicMock()
    return GameLogic(game_repository=mock_game_repo, game_state_repository=mock_game_state_repo, player_repository=mock_player_repo)

@pytest.mark.asyncio
async def test_check_win_condition(game_logic):
    game_id = 1
    game_state_id = 1
    #Mock game 
    mock_game = MagicMock()
    mock_game.id = game_id
    mock_game.players = [Player(id=1, name="Player1", game_id = game_id , game_state_id = game_state_id, host=True, winner = False)]
    
    #Mock session
    mock_session = MagicMock()
    
    #Mock handle win
    with patch.object(game_logic, 'handle_win', return_value = None) as mock_handle_win:
        result = await game_logic.check_win_condition(mock_game, mock_session)
    
        mock_handle_win.assert_called_once_with(mock_game.id, mock_game.players[0] ,mock_session)
        assert result
    
@pytest.mark.asyncio
@patch('game.game_logic.manager', new_callable=AsyncMock)
async def test_handle_win(mock_manager, game_logic):
    game_id = 1
    game_state_id = 1

    last_player = Player(id=6, name="Haerin", game_id = game_id , game_state_id = game_state_id, host=True, winner = False)
    
    mock_session = MagicMock()

    game_logic.game_state_repo.update_game_state.return_value = None
    game_logic.player_repo.assign_winner_of_game.return_value = None
        
    await game_logic.handle_win(game_id, last_player, mock_session)
    
    game_logic.game_state_repo.update_game_state.assert_called_once_with(1, StateEnum.FINISHED, mock_session)
    game_logic.player_repo.assign_winner_of_game.assert_called_once_with(last_player, mock_session)
    
    mock_manager.broadcast.assert_called_once_with({
        "type": "PLAYER_WINNER",
        "game_id": game_id,
        "winner_id": last_player.id,
        "winner_name": last_player.name
    })

    
    

    
import pytest
from unittest.mock import MagicMock, patch
from movementCards.movement_cards_logic import MovementCardLogic
from movementCards.models import typeEnum


@pytest.fixture
def mov_cards_logic():
    mock_mov_cards_repo = MagicMock()
    mock_player_repo = MagicMock()
    return MovementCardLogic(mov_card_repo=mock_mov_cards_repo, player_repo=mock_player_repo)

def test_create_mov_deck(mov_cards_logic):
    mock_session = MagicMock()
    game_id = 1
    
    with patch('random.shuffle', lambda x: x):
        response = mov_cards_logic.create_mov_deck(mock_session, game_id)
    
    assert response == {"message": "Movement deck created and assigned to players"}
    
    expected_calls = [
        ((game_id, typeEnum.DIAGONAL_CONT, mock_session),),
        ((game_id, typeEnum.DIAGONAL_ESP, mock_session),),
        ((game_id, typeEnum.EN_L_DER, mock_session),),
        ((game_id, typeEnum.EN_L_IZQ, mock_session),),
        ((game_id, typeEnum.LINEAL_AL_LAT, mock_session),),
        ((game_id, typeEnum.LINEAL_CONT, mock_session),),
        ((game_id, typeEnum.LINEAL_ESP, mock_session),)      
    ] * 7

    # mov_cards_logic.mov_card_repo.create_movement_card.assert_has_calls(expected_calls, any_order=True)
    
    # me fijo que tenga 49 llamadas
    assert mov_cards_logic.mov_card_repo.create_movement_card.call_count == len(expected_calls)
    
    
    
import pytest
from unittest.mock import MagicMock, patch
from movementCards.utils import MovementCardUtils
from movementCards.models import typeEnum



@pytest.fixture
def mov_cards_utils():
    mock_mov_cards_repo = MagicMock()
    return MovementCardUtils(mov_card_repo=mock_mov_cards_repo)

def test_create_mov_deck(mov_cards_utils):
    mock_session = MagicMock()
    game_id = 1
    
    with patch('random.shuffle', lambda x: x):
        response = mov_cards_utils.create_mov_deck(mock_session, game_id)
    
    assert response == {"message": "Movement deck created"}
    
    expected_calls = [
        ((game_id, typeEnum.DIAGONAL_CONT, mock_session),),
        ((game_id, typeEnum.DIAGONAL_ESP, mock_session),),
        ((game_id, typeEnum.EN_L_DER, mock_session),),
        ((game_id, typeEnum.EN_L_IZQ, mock_session),),
        ((game_id, typeEnum.LINEAL_AL_LAT, mock_session),),
        ((game_id, typeEnum.LINEAL_CONT, mock_session),),
        ((game_id, typeEnum.LINEAL_ESP, mock_session),)      
    ] * 7
    mov_cards_utils.mov_card_repo.create_movement_card.assert_has_calls(expected_calls, any_order=True)
        
    
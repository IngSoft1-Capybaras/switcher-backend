import pytest
from unittest.mock import MagicMock, patch
from figureCards.figure_cards_logic import FigureCardsLogic
from figureCards.models import typeEnum
from player.player_logic import PlayerLogic

@pytest.fixture
def player_repo():
    return MagicMock()

@pytest.fixture
def fig_cards_logic(player_repo):
    mock_fig_cards_repo = MagicMock()
    return FigureCardsLogic(player_repo=player_repo ,fig_card_repo=mock_fig_cards_repo)

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
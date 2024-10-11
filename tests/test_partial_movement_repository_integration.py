import pytest
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

from board.board_repository import BoardRepository
from board.schemas import BoardPosition
from database.db import engine

from game.models import Game
from gameState.models import GameState, StateEnum
from player.models import Player
from movementCards.models import MovementCard, typeEnum
from partial_movement.models import PartialMovements

from partial_movement.partial_movement_repository import PartialMovementRepository

#Configuración de la sesión
Session = sessionmaker(bind=engine)

@pytest.fixture
def partial_movement_repository():
    return PartialMovementRepository()

@pytest.fixture
def session():
    session = Session()
    yield session
    session.close()

@pytest.fixture
def setup_game_player_card(session):
    game = Game(name='name', min_players=2, max_players=3)
    session.add(game)
    session.commit()

    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()

    player = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add(player)
    session.commit()

    card = MovementCard(player_id = player.id ,game_id=game.id,type=typeEnum.DIAGONAL_CONT, description = '', used= False)
    session.add(card)
    session.commit()
    
    return game, player, card

@pytest.mark.integration_test
def test_create_partial_movement(partial_movement_repository, session, setup_game_player_card):
    game, player, card = setup_game_player_card
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))

    # Call the method to create a partial movement
    partial_movement_repository.create_partial_movement(game.id, player.id, card.id, pos_from, pos_to, session)

    # Verify that the partial movement was created
    partial_movement = session.query(PartialMovements).filter_by(game_id=game.id, player_id=player.id, mov_card_id=card.id).one()
    assert partial_movement.pos_from_x == pos_from.pos[0]
    assert partial_movement.pos_from_y == pos_from.pos[1]
    assert partial_movement.pos_to_x == pos_to.pos[0]
    assert partial_movement.pos_to_y == pos_to.pos[1]

@pytest.mark.integration_test
def test_create_partial_movement_no_game(partial_movement_repository, session):
    non_existent_game_id = 9999
    non_existent_player_id = 9999
    non_existent_card_id = 9999
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))

    # Verificamos el error al no encontrar el juego deseado
    with pytest.raises(HTTPException) as exc_info:
        partial_movement_repository.create_partial_movement(non_existent_game_id, non_existent_player_id, non_existent_card_id, pos_from, pos_to, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Game not found"

@pytest.mark.integration_test
def test_create_partial_movement_no_player(partial_movement_repository, session):
    game = Game(name='name', min_players=2, max_players=3)
    session.add(game)
    session.commit()
    
    non_existent_player_id = 9999
    non_existent_card_id = 9999
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))

    # Verificamos el error al no encontrar el jugador deseado
    with pytest.raises(HTTPException) as exc_info:
        partial_movement_repository.create_partial_movement(game.id, non_existent_player_id, non_existent_card_id, pos_from, pos_to, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Player not found in the specified game"
    
@pytest.mark.integration_test
def test_create_partial_movement_player_not_in_game(partial_movement_repository, session):
    game = Game(name='my game', min_players=2, max_players=3)
    session.add(game)
    session.commit()
    
    player_game = Game(name='player game', min_players=2, max_players=3)
    session.add(player_game)
    session.commit()
    
    game_state = GameState(game_id = player_game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()

    player = Player(name="Player1", game_id=player_game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add(player)
    session.commit()
    
    non_existent_card_id = 9999
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))

    # Verificamos el error al no encontrar el jugador deseado
    with pytest.raises(HTTPException) as exc_info:
        partial_movement_repository.create_partial_movement(game.id, player.id, non_existent_card_id, pos_from, pos_to, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Player not found in the specified game"

@pytest.mark.integration_test
def test_create_partial_movement_card_not_in_player_hand(partial_movement_repository, session):
    game = Game(name='name', min_players=2, max_players=3)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()

    player1 = Player(name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add(player1)
    session.commit()
    
    player2 = Player(name="Player2", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    session.add(player2)
    session.commit()
    
    card = MovementCard(player_id = player2.id ,game_id=game.id,type=typeEnum.DIAGONAL_CONT, description = '', used= False)
    session.add(card)
    session.commit()
    
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))

    # Verificamos el error al no encontrar la carta
    with pytest.raises(HTTPException) as exc_info:
        partial_movement_repository.create_partial_movement(game.id, player1.id, card.id, pos_from, pos_to, session)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Card not found for the specified player and game" 


    
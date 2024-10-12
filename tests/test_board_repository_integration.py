import os

import pytest
import logging
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker

from board.board_repository import BoardRepository
from board.models import Board, Box, ColorEnum
from board.schemas import BoardOut, BoardAndBoxesOut, BoxOut, BoardPosition
from database.db import Base, engine
from game.game_repository import GameRepository
from game.models import Game
from game.schemas import GameCreate
from gameState.game_state_repository import GameStateRepository
from player.schemas import PlayerCreateMatch

logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR) # Para evitar que se muestren los logs de SQL Alchemy, setear en INFO para ver comportamiento anterior

#Configuración de la sesión
Session = sessionmaker(bind=engine)

@pytest.fixture
def board_repository():
    return BoardRepository()


@pytest.fixture
def game_repository():
    return GameRepository()

@pytest.fixture
def game_state_repository():
    return GameStateRepository()

@pytest.fixture(autouse=True)
def close_session(session):
    yield
    session.close()


@pytest.mark.integration_test
def test_create_new_board(board_repository: BoardRepository, session):
    N_boards = session.query(Board).filter(Board.game_id == 1).count()
    
    board_repository.create_new_board(1, session)
    
    assert session.query(Board).filter(Board.game_id == 1).count() == N_boards + 1


@pytest.mark.integration_test
def test_get_board(board_repository: BoardRepository, session):
    board = board_repository.get_existing_board(1, session)

    assert isinstance(board, BoardOut)
    assert board.game_id == 1
    

@pytest.mark.integration_test
def test_create_new_board_for_existing_game(game_repository: GameRepository, board_repository: BoardRepository, session):
    # creo un nuevo juego sin tablero
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    new_game = res.get('game')

    # le creo un tablero al juego
    board = board_repository.create_new_board(new_game.id, session)
    
    assert isinstance(board, BoardOut)
    assert board.game_id == new_game.id


@pytest.mark.integration_test
def test_create_new_board_for_non_existing_game(board_repository: BoardRepository, session):
    with pytest.raises(HTTPException) as exc_info:
        board_repository.create_new_board(999, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Game not found"


@pytest.mark.integration_test
def test_get_configured_board_for_non_existing_game(board_repository: BoardRepository, session):
    with pytest.raises(HTTPException) as exc_info:
        board_repository.get_configured_board(999, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Game not found"


@pytest.mark.integration_test
def test_get_configured_board_for_game_not_started(board_repository: BoardRepository, game_repository: GameRepository, session):
    # creo un nuevo juego sin tablero
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    new_game = res.get('game')

    with pytest.raises(HTTPException) as exc_info:
        board_repository.get_configured_board(new_game.id, session)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Game not started"


@pytest.mark.integration_test
def test_get_configured_board_for_game_with_no_board(   board_repository: BoardRepository, 
                                                        game_repository: GameRepository,
                                                        game_state_repository: GameStateRepository, 
                                                        session):
    # creo un nuevo juego sin tablero
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    new_game = res.get('game')

    # inicializo el juego
    game_state_repository.update_game_state(new_game.id, "PLAYING", session)

    with pytest.raises(HTTPException) as exc_info:
        board_repository.get_configured_board(new_game.id, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Board not found"


@pytest.mark.integration_test
def test_get_configured_board_for_board_not_configured(board_repository: BoardRepository, game_repository: GameRepository, game_state_repository: GameStateRepository, session):
    # creo un nuevo juego sin tablero
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    new_game = res.get('game')

    # inicializo el juego
    game_state_repository.update_game_state(new_game.id, "PLAYING", session)

    # creo un tablero
    board_repository.create_new_board(new_game.id, session)

    with pytest.raises(HTTPException) as exc_info:
        board_repository.get_configured_board(new_game.id, session)
    
    assert exc_info.value.status_code == 404
    # assert it contains the string "Boxes not found in row "
    assert "Boxes not found in row " in exc_info.value.detail


@pytest.mark.integration_test
def test_get_configured_board(board_repository: BoardRepository, game_state_repository: GameStateRepository, session):
    
    # obtengo partida existente (asumiendo que ya esta creada)
    game = session.query(Game).first()
    # obtengo el tablero existente (asumiendo que ya esta creado)
    board = board_repository.get_existing_board(game.id, session)
    # mockeo iniciarlo
    game_state_repository.update_game_state(game.id, "PLAYING", session)
    # obtengo el tablero y toda la info de sus boxes (asumiendo que ya esta configurado)
    configured_board = board_repository.get_configured_board(game.id, session)
    
    assert isinstance(configured_board, BoardAndBoxesOut)
    assert configured_board.game_id is not None
    assert configured_board.board_id is not None
    assert len(configured_board.boxes) == 6
    for row in configured_board.boxes:
        assert len(row) == 6
        for box in row:
            assert isinstance(box, BoxOut)
            assert box.color.name in [color.name for color in [ColorEnum.BLUE, ColorEnum.GREEN, ColorEnum.RED, ColorEnum.YELLOW]]
            assert box.pos_x in range(6)
            assert box.pos_y in range(6)
    assert configured_board.game_id == game.id
    assert configured_board.board_id == board.id


@pytest.mark.integration_test
def test_get_not_configured_board(  board_repository: BoardRepository, 
                                    game_repository: GameRepository, 
                                    game_state_repository: GameStateRepository, 
                                    session):

    # crear partida sin tablero configurado
    new_game = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2),
                                PlayerCreateMatch(name="Test Player"),
                                session).get('game')

    # inicializarla en estado PLAYING
    game_state_repository.update_game_state(new_game.id, "PLAYING", session)
    
    with pytest.raises(HTTPException) as exc_info:
        board_repository.get_configured_board(new_game.id, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Board not found"


@pytest.mark.integration_test
def test_add_box_to_existing_board(board_repository: BoardRepository, session):
    # busco un tablero que exista
    existing_board = session.query(Board).first()

    initial_box_count = session.query(Box).filter(Box.board_id == existing_board.id).count()
    
    board_repository.add_box_to_board(existing_board.id, existing_board.game_id, ColorEnum.BLUE, 5, 5, session)
    
    new_box_count = session.query(Box).filter(Box.board_id == existing_board.id).count()
    assert new_box_count == initial_box_count + 1


@pytest.mark.integration_test
def test_switch_boxes(game_repository: GameRepository, board_repository: BoardRepository, session):
    # Crear una partida y un tablero
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    game = res.get('game')
    
    board = board_repository.create_new_board(game.id, session)

    # Creo dos casillas
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))
    board_repository.add_box_to_board(board.id, game.id, ColorEnum.BLUE, pos_from.pos[0], pos_from.pos[1], session)
    board_repository.add_box_to_board(board.id, game.id, ColorEnum.RED, pos_to.pos[0], pos_to.pos[1], session)

    # Verifico colores iniciales
    box_from = session.query(Box).filter(Box.board_id == board.id, Box.pos_x == pos_from.pos[0], Box.pos_y == pos_from.pos[1]).one()
    box_to = session.query(Box).filter(Box.board_id == board.id, Box.pos_x == pos_to.pos[0], Box.pos_y == pos_to.pos[1]).one()
    assert box_from.color == ColorEnum.BLUE
    assert box_to.color == ColorEnum.RED

    # Hacemos el intercambio
    board_repository.switch_boxes(game.id, pos_from, pos_to, session)

    # Verificamos el intercambio
    box_from = session.query(Box).filter(Box.board_id == board.id, Box.pos_x == pos_from.pos[0], Box.pos_y == pos_from.pos[1]).one()
    box_to = session.query(Box).filter(Box.board_id == board.id, Box.pos_x == pos_to.pos[0], Box.pos_y == pos_to.pos[1]).one()
    assert box_from.color == ColorEnum.RED
    assert box_to.color == ColorEnum.BLUE

@pytest.mark.integration_test
def test_switch_boxes_inexistent_box_from(board_repository: BoardRepository, game_repository: GameRepository, session):
    # Crear una partida y un tablero
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    game = res.get('game')
    
    board = board_repository.create_new_board(game.id, session)

    # Creo una casillaa
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))
    board_repository.add_box_to_board(board.id, game.id, ColorEnum.RED, pos_to.pos[0], pos_to.pos[1], session)

    # Hacemos el intercambio

    with pytest.raises(HTTPException) as exc_info:
        board_repository.switch_boxes(game.id, pos_from, pos_to, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Box not found"


@pytest.mark.integration_test
def test_switch_boxes_inexistent_box_from(board_repository: BoardRepository, game_repository: GameRepository, session):
        # Crear una partida y un tablero
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    game = res.get('game')
    
    board = board_repository.create_new_board(game.id, session)

    # Creo una casilla
    pos_from = BoardPosition(pos=(0, 0))
    board_repository.add_box_to_board(board.id, game.id, ColorEnum.BLUE, pos_from.pos[0], pos_from.pos[1], session)

    pos_to = BoardPosition(pos=(1, 1))

    # Hacemos el intercambio

    with pytest.raises(HTTPException) as exc_info:
        board_repository.switch_boxes(game.id, pos_from, pos_to, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Box not found"
    
@pytest.mark.integration_test
def test_switch_boxes_inexistent_game(board_repository: BoardRepository, session):
    # id de juego que no existe
    game_id = 13434242
    

    # Creo una casilla
    pos_from = BoardPosition(pos=(0, 0))
    pos_to = BoardPosition(pos=(1, 1))

    # Hacemos el intercambio

    with pytest.raises(HTTPException) as exc_info:
        board_repository.switch_boxes(game_id, pos_from, pos_to, session)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"Game not found"
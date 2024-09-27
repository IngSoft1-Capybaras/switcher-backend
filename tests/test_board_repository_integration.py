import pytest
from sqlalchemy.orm import sessionmaker
from board.board_repository import BoardRepository
from board.models import  ColorEnum, Board, Box
from board.schemas import BoardOut
from figureCards.models import FigureCard
from game.models import Game
from game.schemas import GameCreate
from game.game_repository import GameRepository
from gameState.models import GameState
from movementCards.models import MovementCard
from player.models import Player
from player.schemas import PlayerCreateMatch
from fastapi import HTTPException

from database.db import engine, Base
import os

#Configuración de la sesión
Session = sessionmaker(bind=engine)


@pytest.fixture
def board_repository():
    return BoardRepository()


@pytest.fixture
def game_repository():
    return GameRepository()


@pytest.mark.integration_test
def test_create_new_board(board_repository: BoardRepository, session):
    # session = Session()
    
    # try:
    N_boards = session.query(Board).filter(Board.game_id == 1).count()
    # finally:
    #     session.close()
    
    board_repository.create_new_board(1,session)
    
    # session = Session()
    
    # try:
    assert session.query(Board).filter(Board.game_id == 1).count() == N_boards + 1
    # finally:
    #     session.close()
        

@pytest.mark.integration_test
def test_get_board(board_repository: BoardRepository, session):
    # session = Session()
    
    # try:
    board = board_repository.get_existing_board(1, session)
    assert board is not None
    # finally:
    #     session.close()


# @pytest.mark.integration_test
# def test_add_box_to_board(board_repository: BoardRepository, session):
#     # session = Session()
    
#     # try:
#     N_boxes = session.query(Box).filter(Box.board_id == 1).count()
#     # finally:
#     #     session.close()
    
#     board_repository.add_box_to_board(1, 1, ColorEnum.YELLOW, 4, 3, session)
    
#     # session = Session()
    
#     # try:
#     assert session.query(Box).filter(Box.board_id == 1).count() == N_boxes + 1
#     # finally:
#     #     session.close()
        

@pytest.mark.integration_test
def test_configure_board(board_repository: BoardRepository, session):
    # session = Session()
    
    # try:
    N_boxes = session.query(Box).filter(Box.game_id == 99).count()
    # finally:
    #     session.close()
    board_repository.configure_board(99, session)
    
    # session = Session()
    
    # try:
    assert session.query(Box).filter(Box.game_id == 99).count() == N_boxes + 36
    # finally:
    #     session.close()



@pytest.mark.integration_test
def test_get_existing_board_for_populated_game(board_repository: BoardRepository, session):
    game = session.query(Game).first()
    
    result = board_repository.get_existing_board(game.id, session)
    
    assert isinstance(result, BoardOut)
    assert result.game_id == game.id


@pytest.mark.integration_test
def test_create_new_board_for_existing_game(game_repository: GameRepository, board_repository: BoardRepository, session):
    # Create a new game without a board
    res = game_repository.create_game(GameCreate(name="Test Game 2", max_players=4, min_players=2),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    new_game = res.get('game')

    board = board_repository.create_new_board(new_game.id, session)
    
    assert board is not None
    assert board.game_id == new_game.id


@pytest.mark.integration_test
def test_add_box_to_existing_board(board_repository: BoardRepository, session):
    # Get an existing board
    existing_board = session.query(Board).first()
    print(f"id de board {existing_board.id}")

    initial_box_count = session.query(Box).filter(Box.board_id == existing_board.id).count()
    
    board_repository.add_box_to_board(existing_board.id, existing_board.game_id, ColorEnum.BLUE, 5, 5, session)
    
    new_box_count = session.query(Box).filter(Box.board_id == existing_board.id).count()
    assert new_box_count == initial_box_count + 1


@pytest.mark.integration_test
def test_configure_board_for_new_game(game_repository: GameRepository, board_repository: BoardRepository, session):
    # Create a new game without a board
    res = game_repository.create_game(GameCreate(name="Another test game", max_players=4, min_players=2),
                                PlayerCreateMatch(name="Test Player"),
                                session)
    new_game = res.get('game')

    
    result = board_repository.configure_board(new_game.id, session)
    
    assert result == {"message": "Board created successfully"}
    
    new_board = session.query(Board).filter(Board.game_id == new_game.id).first()
    assert new_board is not None
    
    box_count = session.query(Box).filter(Box.board_id == new_board.id).count()
    assert box_count == 36


@pytest.mark.integration_test
def test_configure_board_color_distribution(game_repository: GameRepository, board_repository: BoardRepository, session):
    # Create a new game without a board
    res = game_repository.create_game(GameCreate(name="Color Distribution Test Game", max_players=4, min_players=2),
                            PlayerCreateMatch(name="Test Player"),
                            session)
    new_game = res.get('game')

    board_repository.configure_board(new_game.id, session)
    
    new_board = session.query(Board).filter(Board.game_id == new_game.id).first()
    boxes = session.query(Box).filter(Box.board_id == new_board.id).all()
    
    color_counts = {color: 0 for color in ColorEnum}
    for box in boxes:
        color_counts[box.color] += 1
    
    assert all(count == 9 for count in color_counts.values())


@pytest.mark.integration_test
def test_configure_board_already_configured(board_repository: BoardRepository, session):
    # Get an existing game that already has a board
    existing_game = session.query(Game).join(Board).first()
    
    with pytest.raises(HTTPException) as exc_info:
        board_repository.configure_board(existing_game.id, session)
    
    assert exc_info.value.status_code == 400
    assert "Board already exists" in str(exc_info.value.detail)
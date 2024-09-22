import pytest
from sqlalchemy.orm import sessionmaker
from .board_repository import BoardRepository
from .models import  ColorEnum, Board, Box
from figureCards.models import FigureCard
from game.models import Game
from gameState.models import GameState
from movementCards.models import MovementCard
from player.models import Player

from database.db import engine, Base
import os

#Configuración de la sesión
Session = sessionmaker(bind=engine)

@pytest.fixture(scope='session', autouse=True)
def setup_and_teardown_db():
    # Create all tables 
    Base.metadata.create_all(engine)
    yield
    # Drop all tables after  tests
    Base.metadata.drop_all(engine)
    
    if os.path.exists("db_test.sqlite"):
        os.remove("db_test.sqlite")


@pytest.fixture
def board_repository():
    return BoardRepository()


def test_create_new_board(board_repository: BoardRepository):
    session = Session()
    
    try:
        N_boards = session.query(Board).filter(Board.game_id == 1).count()
    finally:
        session.close()
    
    board_repository.create_new_board(1)
    
    session = Session()
    
    try:
        assert session.query(Board).filter(Board.game_id == 1).count() == N_boards + 1
    finally:
        session.close()
        

def test_get_board(board_repository: BoardRepository):
    session = Session()
    
    try:
        board = board_repository.get_existing_board(1)
        assert board is not None
    finally:
        session.close()


def test_add_box_to_board(board_repository: BoardRepository):
    session = Session()
    
    try:
        N_boxes = session.query(Box).filter(Box.board_id == 1).count()
    finally:
        session.close()
    
    board_repository.add_box_to_board(1,1,ColorEnum.YELLOW, 4, 3)
    
    session = Session()
    
    try:
        assert session.query(Box).filter(Box.board_id == 1).count() == N_boxes + 1
    finally:
        session.close()
        

def test_configure_board(board_repository: BoardRepository):
    session = Session()
    
    try:
        N_boxes = session.query(Box).filter(Box.game_id == 2).count()
    finally:
        session.close()
    
    board_repository.configure_board(2)
    
    session = Session()
    
    try:
        assert session.query(Box).filter(Box.game_id == 2).count() == N_boxes + 36
    finally:
        session.close()





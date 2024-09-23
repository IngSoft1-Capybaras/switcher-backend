import pytest
from sqlalchemy.orm import sessionmaker
from board.board_repository import BoardRepository
from board.models import  ColorEnum, Board, Box
from figureCards.models import FigureCard
from game.models import Game
from gameState.models import GameState
from movementCards.models import MovementCard
from player.models import Player

from database.db import engine, Base
import os

#Configuración de la sesión
Session = sessionmaker(bind=engine)


@pytest.fixture
def board_repository():
    return BoardRepository()

@pytest.mark.integration_test
def test_create_new_board(board_repository: BoardRepository):
    session = Session()
    
    try:
        N_boards = session.query(Board).filter(Board.game_id == 1).count()
    finally:
        session.close()
    
    board_repository.create_new_board(1,session)
    
    session = Session()
    
    try:
        assert session.query(Board).filter(Board.game_id == 1).count() == N_boards + 1
    finally:
        session.close()
        
@pytest.mark.integration_test
def test_get_board(board_repository: BoardRepository):
    session = Session()
    
    try:
        board = board_repository.get_existing_board(1, session)
        assert board is not None
    finally:
        session.close()

@pytest.mark.integration_test
def test_add_box_to_board(board_repository: BoardRepository):
    session = Session()
    
    try:
        N_boxes = session.query(Box).filter(Box.board_id == 1).count()
    finally:
        session.close()
    
    board_repository.add_box_to_board(1,1,ColorEnum.YELLOW, 4, 3, session)
    
    session = Session()
    
    try:
        assert session.query(Box).filter(Box.board_id == 1).count() == N_boxes + 1
    finally:
        session.close()
        
@pytest.mark.integration_test
def test_configure_board(board_repository: BoardRepository):
    session = Session()
    
    try:
        N_boxes = session.query(Box).filter(Box.game_id == 4).count()
    finally:
        session.close()
    
    board_repository.configure_board(4, session)
    
    session = Session()
    
    try:
        assert session.query(Box).filter(Box.game_id == 4).count() == N_boxes + 36
    finally:
        session.close()





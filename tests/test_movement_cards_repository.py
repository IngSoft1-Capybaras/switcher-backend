import pytest
from sqlalchemy.orm import sessionmaker
from movementCards.movement_cards_repository import MovementCardsRepository
from board.models import  Board, Box
from figureCards.models import FigureCard
from game.models import Game
from gameState.models import GameState
from movementCards.models import MovementCard, typeEnum
from figureCards.models import FigureCard
from player.models import Player

from database.db import engine

#Configuración de la sesión
Session = sessionmaker(bind=engine)

@pytest.fixture
def movement_card_repository():
    return MovementCardsRepository()

@pytest.mark.integration_test
def test_create_new_movement_card(movement_card_repository: MovementCardsRepository):
    session = Session()
    
    try:
        N_cards = session.query(MovementCard).filter(MovementCard.game_id == 1).count()
    finally:
        session.close()
    
    movement_card_repository.create_movement_card(1, typeEnum.EN_L_DER, session)
    
    session = Session()
    
    try:
        assert session.query(MovementCard).filter(MovementCard.game_id == 1).count() == N_cards + 1
    finally:
        session.close()
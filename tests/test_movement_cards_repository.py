import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
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
def movement_cards_repository():
    return MovementCardsRepository()


@pytest.mark.integration_test
def test_get_movement_cards(movement_cards_repository: MovementCardsRepository, session):
    # session = Session()
    # try:
    N_cards = session.query(MovementCard).filter(MovementCard.game_id == 1, 
                                                MovementCard.player_id == 1).count()

    list_of_cards = movement_cards_repository.get_movement_cards(1, 1, session)
    
    assert len(list_of_cards) == N_cards

    # finally:
    #     session.close()


@pytest.mark.integration_test
def test_get_movement_card_by_id(movement_cards_repository: MovementCardsRepository, session):
    # session = Session()
    try:
        # busco la cantidad de cartas con todos id 1
        test_card = session.query(MovementCard).filter(MovementCard.game_id == 1,
                                                  MovementCard.player_id == 1,
                                                  MovementCard.id == 1).one()
        
        movement_card = movement_cards_repository.get_movement_card_by_id(1, 1, 1, session)

        assert test_card.id == movement_card.id
    except NoResultFound:
        raise ValueError("There is no movement card with game_id=1, player_id=1 and id=1")
    # finally:
    #     session.close()


@pytest.mark.integration_test
def test_create_new_movement_card(movement_cards_repository: MovementCardsRepository, session):
    # session = Session()
    
    # try:
    N_cards = session.query(MovementCard).filter(MovementCard.game_id == 1).count()
    # finally:
    #     session.close()
    
    movement_cards_repository.create_movement_card(1, typeEnum.EN_L_DER, session)
    # session = Session()
    
    # try:
    assert session.query(MovementCard).filter(MovementCard.game_id == 1).count() == N_cards + 1
    # finally:
    #     session.close()
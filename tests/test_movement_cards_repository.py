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
from fastapi import HTTPException

from database.db import engine

#Configuración de la sesión
Session = sessionmaker(bind=engine)

@pytest.fixture
def movement_cards_repository():
    return MovementCardsRepository()


@pytest.mark.integration_test
def test_get_movement_cards(movement_cards_repository: MovementCardsRepository, session):
    N_cards = session.query(MovementCard).filter(MovementCard.game_id == 1, 
                                                MovementCard.player_id == 1).count()

    list_of_cards = movement_cards_repository.get_movement_cards(1, 1, session)
    
    assert len(list_of_cards) == N_cards


@pytest.mark.integration_test
def test_get_movement_cards_no_cards(movement_cards_repository: MovementCardsRepository, session):
    # uso un game_id y player_id exageradamente grande para que salte la exception
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.get_movement_cards(999, 999, session)
    
    assert excinfo.value.status_code == 404
    assert "There no movement cards associated with this game and player" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_get_movement_card_by_id(movement_cards_repository: MovementCardsRepository, session):
    try:
        # busco la cantidad de cartas con todos id 1
        test_card = session.query(MovementCard).filter(MovementCard.game_id == 1,
                                                  MovementCard.player_id == 1,
                                                  MovementCard.id == 1).one()
        
        movement_card = movement_cards_repository.get_movement_card_by_id(1, 1, 1, session)
    except NoResultFound:
        raise ValueError("There is no movement card with game_id=1, player_id=1 and id=1")
    
    assert test_card.id == movement_card.id


@pytest.mark.integration_test
def test_get_movement_card_by_id_not_found(movement_cards_repository: MovementCardsRepository, session):
    # uso un mov_card_id exageradamente grande para que salte la exception
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.get_movement_card_by_id(1, 1, 999, session)
    
    assert excinfo.value.status_code == 404
    assert "Movement card not found" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_create_new_movement_card(movement_cards_repository: MovementCardsRepository, session):
    N_cards = session.query(MovementCard).filter(MovementCard.game_id == 1).count()
    
    movement_cards_repository.create_movement_card(1, typeEnum.EN_L_DER, session)
    
    assert session.query(MovementCard).filter(MovementCard.game_id == 1).count() == N_cards + 1


@pytest.mark.integration_test
def test_create_movement_card_invalid_type(movement_cards_repository: MovementCardsRepository, session):
    # Cuento cuantas cartas tiene el game 1 antes de crear una nueva carta
    N_cards = session.query(MovementCard).filter(MovementCard.game_id == 1).count()

    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.create_movement_card(1, "INVALID_TYPE", session)

    # Me fijo que no se haya creado ninguna carta de movimiento
    assert session.query(MovementCard).filter(MovementCard.game_id == 1).count() == N_cards
    assert excinfo.value.status_code == 400 # Me fijo que de BAD REQUEST
    assert "Incorrect type for movement card: INVALID_TYPE" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_create_movement_card_with_invalid_game_id(movement_cards_repository: MovementCardsRepository, session):
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.create_movement_card(-1, typeEnum.EN_L_DER, session)

    assert excinfo.value.status_code == 404


@pytest.mark.integration_test
def test_get_movement_cards_deck(movement_cards_repository: MovementCardsRepository, session):
    N_cards = session.query(MovementCard).filter(MovementCard.game_id == 1, 
                                                 MovementCard.player_id.is_(None)).count()

    movement_deck = movement_cards_repository.get_movement_deck(1, session)

    assert N_cards == len(movement_deck)


@pytest.mark.integration_test
def test_get_movement_deck_no_cards(movement_cards_repository: MovementCardsRepository, session):
    # uso un game_id exageradamente grande para que salte la exception
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.get_movement_deck(999, session)
    
    assert excinfo.value.status_code == 404
    assert "There no movement cards associated with this game" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_assign_mov_card(movement_cards_repository: MovementCardsRepository, session):
    # busco la primer carta de movimiento que encuentre que no tenga un player asignado
    test_card = session.query(MovementCard).filter(MovementCard.player_id == None).first()

    # Le asigno el player 1 a la carta
    movement_cards_repository.assign_mov_card(test_card.id, 1, session)

    
    assert test_card.player_id == 1
    assert test_card.used == False # Me aseguro que la flag used no haya sido cambiada


@pytest.mark.integration_test
def test_discard_mov_card(movement_cards_repository: MovementCardsRepository, session):
    # busco la carta de movimiento con id 1 que se que tiene al player 1
    try:
        test_card = session.query(MovementCard).filter(MovementCard.id == 1).one()
    except NoResultFound:
        raise ValueError("There is no movement card with id 1")
    
    # Le asigno el player 1 a la carta
    movement_cards_repository.discard_mov_card(test_card.id, session)

    
    assert test_card.player_id == None # Me fijo que la carta no tenga mas duenio
    assert test_card.used == True # Me fijo que la carta esta como usada


# dejar este test debajo del discard_mov_card, asi se descarta la unica carta sin player y no da error la query
@pytest.mark.integration_test
def test_assign_mov_card_invalid_player(movement_cards_repository: MovementCardsRepository, session):
    # busco la primer carta de movimiento que encuentre que no tenga un player asignado
    test_card = session.query(MovementCard).filter(MovementCard.player_id == None).first()

    # uso un player_id exageradamente grande para que salte la exception
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.assign_mov_card(test_card.id, 999, session)
    
    assert excinfo.value.status_code == 404
    assert "no player with specified id" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_assign_mov_card_invalid_card(movement_cards_repository: MovementCardsRepository, session):
    # uso un mov_card_id exageradamente grande para que salte la exception
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.assign_mov_card(999, 1, session)

    assert excinfo.value.status_code == 404
    assert "There no movement cards associated with this game" in str(excinfo.value.detail)


@pytest.mark.integration_test
def test_discard_mov_card_invalid_card(movement_cards_repository: MovementCardsRepository, session):
    # uso un mov_card_id exageradamente grande para que salte la exception
    with pytest.raises(HTTPException) as excinfo:
        movement_cards_repository.discard_mov_card(999, session)

    assert excinfo.value.status_code == 404
    assert f"There no movement cards associated with this id 999" in str(excinfo.value.detail)




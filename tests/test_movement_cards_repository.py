import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from movementCards.movement_cards_repository import MovementCardsRepository
from board.models import  Board, Box
from figureCards.models import FigureCard
from game.models import Game
from gameState.models import GameState, StateEnum
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
    
@pytest.mark.integration_test
def test_grab_mov_cards(movement_cards_repository: MovementCardsRepository, session):
    
    game = Game(name="Test Game", max_players=4, min_players=2)
    session.add(game)
    session.commit()
    
    game_state = GameState(game_id = game.id, state=StateEnum.PLAYING)
    session.add(game_state)
    session.commit()
    
    player1 = Player(id=28, name="Player1", game_id=game.id, game_state_id=game_state.id, host=True, winner=False)
    player2 = Player(id=29, name="Player2", game_id=game.id, game_state_id=game_state.id, host=False, winner=False)
    session.add_all([player1, player2])
    session.commit()
    
    session.add_all([
        MovementCard(player_id = player1.id ,game_id=game.id,type=typeEnum.DIAGONAL_CONT, description = '', used= False),
        MovementCard(player_id = player1.id , game_id=game.id, type=typeEnum.EN_L_DER, description = '', used= False),
        MovementCard(game_id=game.id, type=typeEnum.DIAGONAL_CONT, description = '', used= False),
        MovementCard(player_id = player2.id , game_id=game.id, type=typeEnum.LINEAL_AL_LAT, description = '', used= False),
        MovementCard(game_id=game.id, type=typeEnum.DIAGONAL_CONT, description = '', used= False),
        MovementCard(game_id=game.id, type=typeEnum.DIAGONAL_CONT, description = '', used= False),
        MovementCard(game_id=game.id, type=typeEnum.LINEAL_CONT, description = '', used= False),
        MovementCard(game_id=game.id, type=typeEnum.DIAGONAL_CONT, description = '', used= False),
        MovementCard(game_id=game.id, type=typeEnum.LINEAL_ESP, description = '', used= False)
    ])
    session.commit()
    
    movement_cards_repository.grab_mov_cards(player1.id, game.id, session)
    movement_cards_repository.grab_mov_cards(player2.id, game.id, session)

    shown_cards_player1 = session.query(MovementCard).filter(
        MovementCard.player_id == player1.id,
        MovementCard.game_id == game.id,
    ).all()
    
    shown_cards_player2 = session.query(MovementCard).filter(
        MovementCard.player_id == player2.id,
        MovementCard.game_id == game.id,
    ).all()
    
    assert len(shown_cards_player1) == 3
    assert len(shown_cards_player2) == 3
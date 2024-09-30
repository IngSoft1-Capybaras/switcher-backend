import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from figureCards.figure_cards_repository import FigureCardsRepository
from board.models import  Board, Box
from figureCards.models import FigureCard, typeEnum
from game.models import Game
from gameState.models import GameState
from movementCards.models import MovementCard
from player.models import Player


from database.db import engine

#Configuración de la sesión
Session = sessionmaker(bind=engine)


@pytest.fixture
def figure_cards_repository():
    return FigureCardsRepository()


@pytest.mark.integration_test
def test_get_figure_cards(figure_cards_repository: FigureCardsRepository, session):
    # session = Session()
    # try:
    N_cards = session.query(FigureCard).filter(FigureCard.game_id == 1, 
                                                FigureCard.player_id == 1).count()
    
    list_of_cards = figure_cards_repository.get_figure_cards(1, 1, session)
    
    assert len(list_of_cards) == N_cards

    # finally:
    #     session.close()


@pytest.mark.integration_test
def test_get_figure_card_by_id(figure_cards_repository: FigureCardsRepository, session):
    # session = Session()
    try:
        # busco la cantidad de cartas con todos id 1
        test_card = session.query(FigureCard).filter(FigureCard.game_id == 1,
                                                  FigureCard.player_id == 1,
                                                  FigureCard.id == 1).one()
        
        figure_card = figure_cards_repository.get_figure_card_by_id(1, 1, 1, session)

        assert test_card.id == figure_card.id
    except NoResultFound:
        raise ValueError("There is no figure card with game_id=1, player_id=1 and id=1")
    # finally:
    #     session.close()


@pytest.mark.integration_test
def test_create_new_figure_card(figure_cards_repository: FigureCardsRepository, session):
    # session = Session()
    # try:
    N_cards = session.query(FigureCard).filter(FigureCard.game_id == 1,
                                               FigureCard.player_id == 1).count()
    # finally:
    #     session.close()
    
    figure_cards_repository.create_figure_card(1, 1, typeEnum.TYPE_4, True, session)
    
    # session = Session()
    
    # try:
    assert session.query(FigureCard).filter(FigureCard.player_id == 1).count() == N_cards + 1
    # finally:
    #     session.close()
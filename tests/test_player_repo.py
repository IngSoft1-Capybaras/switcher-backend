import pytest
from player.player_repository import PlayerRepository
from sqlalchemy.orm import sessionmaker
from board.models import  Board, Box
from figureCards.models import FigureCard
from game.models import Game
from gameState.models import GameState
from movementCards.models import MovementCard
from figureCards.models import FigureCard
from player.models import Player, turnEnum

from database.db import engine

#Configuración de la sesión
Session = sessionmaker(bind=engine)


@pytest.fixture
def player_repo():
    return PlayerRepository()


@pytest.mark.integration_test
def test_get_player_by_id(player_repo: PlayerRepository):
    session = Session()
    
    try:
        player = Player(
            name="test_player",
            game_id = 1,
            game_state_id = 1,
            host = False 
        )
        session.add(player)
        session.commit()
        
        player_in_db = player_repo.get_player_by_id(player.game_id, player.id, session)
        
        assert player_in_db.name == player.name
        
    finally:
        session.close()

@pytest.mark.integration_test
def test_get_players_in_game(player_repo: PlayerRepository):
    session = Session()
    
    try:
        player1 = Player(name="player1", game_id=1,game_state_id = 1, host = False )
        player2 = Player(name="player2", game_id=1,game_state_id = 1, host = True )
        session.add(player1)
        session.add(player2)
        session.commit()
        
        N_players = session.query(Player).filter(Player.game_id == 1).count()
    
        players_in_game = player_repo.get_players_in_game(1, session)

        assert len(players_in_game) == N_players

    finally:
        session.close()

@pytest.mark.integration_test     
def test_assign_turn_player(player_repo: PlayerRepository):
    session = Session()
    
    try:
        player = Player(name="player1", game_id=5, host=False)
        session.add(player)
        session.commit()
        
        player_id = player.id
    
    finally:
        session.close()
    
    player_repo.assign_turn_player(player.game_id, player_id, turnEnum.SEGUNDO, session)
    
    session = Session()
    
    try:
        updated_player = session.query(Player).filter(Player.id == player_id).first()
        
        assert updated_player.turn == turnEnum.SEGUNDO
        
    finally:
        session.close()
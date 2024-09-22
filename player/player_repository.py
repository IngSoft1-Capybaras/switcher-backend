from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from .models import Player, turnEnum
from .schemas import PlayerInDB
from database.db import engine


Session = sessionmaker(bind=engine)

class PlayerRepository:
    
    def get_player_by_id(self, player_id: int) -> PlayerInDB:
        session = Session()
        try:
            
            player_in_db = session.query(Player).filter(Player.id == player_id).first()

            if player_in_db:
                return PlayerInDB.model_validate(player_in_db)

        finally:
            session.close()
    
    def get_players_in_game(self, game_id: int) -> dict:
        session = Session()
        try:
            
            players = session.query(Player).filter(Player.game_id == game_id).all()
            if players:
                return [PlayerInDB.model_validate(player) for player in players]

        finally:
            session.close()
    
    def assign_turn_player(self, player_id: int,turn: turnEnum):
        session = Session()

        try:
            player = session.query(Player).filter(Player.id == player_id).first()
            if player:
                player.turn = turn
            session.commit()
            
        finally:
            session.close()
    
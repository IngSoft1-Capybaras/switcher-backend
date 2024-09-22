from multiprocessing import Value
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from .models import GameState, StateEnum
from .schemas import GameStateInDB
from database.db import get_db
from player.models import Player, turnEnum

from database.db import engine


Session = sessionmaker(bind=engine)

class GameStateRepository:
    
    def update_game_state(self, game_id: int, state: StateEnum ):
        session = Session()
        try:
            game_state_instance = session.query(GameState).filter(GameState.idGame == game_id).first()

            game_state_instance.state = state

            session.commit()
        except NoResultFound:
            raise ValueError("Game State does not exist")
        finally:
            session.close()
    
    def update_current_player(self, game_id: int, first_player_id: int):
        session = Session()
        
        try: 
            game_state_instance = session.query(GameState).filter(GameState.idGame == game_id).first()

            game_state_instance.currentPlayer = first_player_id
            session.commit()
        except NoResultFound:
            raise ValueError("Game State does not exist")
        finally:
            session.close()
    
    def get_game_state_by_id(self, game_id: int) -> GameStateInDB:
        session = Session()
        try:
            
            game_state_in_db = session.query(GameState).filter(GameState.idGame == game_id).first()

            if game_state_in_db:
                return GameStateInDB.model_validate(game_state_in_db)

        finally:
            session.close()
        
    def get_next_player_id(self, game_id: int) -> int:
        session = Session()
        
        try:
            game_state_instance = session.query(GameState).filter(GameState.idGame == game_id).first()
            
            if not game_state_instance:
                raise ValueError("Game State does not exist")
            current_player_id = game_state_instance.currentPlayer
            
            players = session.query(Player).filter(Player.game_id == game_id).all()
        
            if not players:
                raise ValueError("No players found for game")
            
            current_player = next((player for player in players if player.id == current_player_id), None)
            
            if not current_player:
                raise ValueError("Current player not found")
            
            current_turn = current_player.turn
            
            turn_order = [
                turnEnum.PRIMERO,
                turnEnum.SEGUNDO,
                turnEnum.TERCERO,
                turnEnum.CUARTO
            ]
            
            current_turn_index = turn_order.index(current_turn)
            next_turn = turn_order[(current_turn_index + 1) % len(turn_order)]
            
            next_player = next((player for player in players if player.turn == next_turn), None)
            
            if not next_player:
                raise ValueError("Next player not found")
            
            return next_player.id
            
            
        finally: 
            session.close()
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from .models import GameState, StateEnum
from .schemas import GameStateInDB
from database.db import get_db
from player.models import Player

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
        
    
    
from sqlalchemy.orm import sessionmaker
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from .models import Game
from .schemas import GameCreate, GameInDB
from database.db import engine


Session = sessionmaker(bind=engine)

class GameRepository:
    
    def get_game_by_id(self, game_id: int):
        session = Session()
        
        try:
            
            game_in_db = session.query(Game).filter(Game.id == game_id).first()

            if game_in_db:
                return GameInDB.model_validate(game_in_db)

        finally:
            session.close()


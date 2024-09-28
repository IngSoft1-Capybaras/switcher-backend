from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from .models import Game
from game.game_repository import GameRepository
from gameState.game_state_repository import GameStateRepository


class GameUtils:
    def __init__(self, game_repository: GameRepository):
         self.game_repository = game_repository

    def count_players_in_game(self, game_id: int, db: Session) -> int:
        try:
            game = db.query(Game).filter(Game.id == game_id).one()
            
        except NoResultFound:
            raise HTTPException(status_code = 404, detail = "Game not found")
        
        player_count = game.players_count()
        return player_count


    def check_win_condition(self, game: Game, db: Session):
            # chequeo si queda solo uno
            players_left = self.count_players_in_game(Game.id)
            if players_left == 1:    
                Game.game_state 

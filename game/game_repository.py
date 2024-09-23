from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from .models import Game
from .schemas import GameCreate, GameInDB
from player.models import Player
from player.schemas import PlayerCreateMatch, PlayerInDB, turnEnum
from gameState.models import GameState, StateEnum
from gameState.schemas import GameStateInDB

class GameRepository:

    def get_games(self, db : Session, limit: int = 5, offset: int = 0) -> list:
        # Fetch games
        games = db.query(Game).offset(offset).limit(limit).all()
        
        if not games:
            raise HTTPException(status_code = 404, detail = "There are no games available")
        
        # Conveert games to a list of shemas
        games_list = [GameInDB.model_validate(game) for game in games]
        
        return games_list
    
    def get_game_by_id(self, game_id: int, db : Session) -> GameInDB:
        
        # Fetch the specifc game by its id
        try:
            game = db.query(Game).filter(Game.id == game_id).one()
        except NoResultFound:
            raise HTTPException(status_code = 404, detail = "Game not found")
        
        # Convert game to schema
        game_schema = GameInDB.model_validate(game)
        
        return game_schema
    
        # Fetch the specifc game by its id
    def create_game(self, game: GameCreate, player: PlayerCreateMatch,db : Session ):
                
        # Create game instance
        game_instance = Game(**game.model_dump())
        db.add(game_instance)
        db.flush()  # Flush to get the game_instance.id

        # Create game state instance
        game_status_instance = GameState(game_id=game_instance.id, state=StateEnum.WAITING)
        db.add(game_status_instance)
        db.flush()  # Flush to get the game_status_instance.id

        # Create player instance
        player_instance = Player(
            name=player.name,
            game_id=game_instance.id,
            game_state_id=game_status_instance.id,
            turn=player.turn or turnEnum.PRIMERO,  # Use provided turn or default to PRIMERO
            host=player.host
        )
        db.add(player_instance)
        db.commit()
        db.refresh(player_instance)

        return {
            "game": GameInDB.model_validate(game_instance),
            "player": PlayerInDB.model_validate(player_instance),
            "gameState": GameStateInDB.model_validate(game_status_instance)
        }

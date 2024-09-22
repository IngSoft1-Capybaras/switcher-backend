from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from .player_repository import PlayerRepository

player_router = APIRouter()

# Get all players of a game
@player_router.get("/players/{game_id}")
def get_players_in_game(game_id: int, db: Session = Depends(get_db), repo: PlayerRepository = Depends()):
    return repo.get_players_in_game(game_id, db)


# Get player by id
@player_router.get("/players/{game_id}/{player_id}")
def get_player_by_id(game_id: int, player_id: int, db: Session = Depends(get_db), repo: PlayerRepository = Depends()):
    return repo.get_player_by_id(game_id, player_id, db)
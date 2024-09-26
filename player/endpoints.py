from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database.db import get_db
from .player_repository import PlayerRepository
from connection_manager import manager

player_router = APIRouter()

# Get all players of a game
@player_router.get("/players/{game_id}")
def get_players_in_game(game_id: int, db: Session = Depends(get_db), repo: PlayerRepository = Depends()):
    return repo.get_players_in_game(game_id, db)


# Get player by id
@player_router.get("/players/{game_id}/{player_id}")
def get_player_by_id(game_id: int, player_id: int, db: Session = Depends(get_db), repo: PlayerRepository = Depends()):
    return repo.get_player_by_id(game_id, player_id, db)

@player_router.post("/players/join/{game_id}", status_code= status.HTTP_201_CREATED)
async def join_game(game_id: int, player_name: str, db: Session = Depends(get_db), repo: PlayerRepository = Depends()):
    player_id = repo.create_player(game_id, player_name, db)
    
    player_list_update = {
            f"{game_id}": "GAME_INFO_UPDATED"
        }
    await manager.broadcast_game(game_id, player_list_update)
        
    return player_id
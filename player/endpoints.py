from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from .player_repository import PlayerRepository
from connection_manager import manager

player_router = APIRouter()

# Obtener todos los jugadores en una partida
@player_router.get("/players/{game_id}")
def get_players_in_game(game_id: int, db: Session = Depends(get_db), repo: PlayerRepository = Depends()):
    return repo.get_players_in_game(game_id, db)


# Obtener jugador por id en una partida
@player_router.get("/players/{game_id}/{player_id}")
def get_player_by_id(game_id: int, player_id: int, db: Session = Depends(get_db), repo: PlayerRepository = Depends()):
    return repo.get_player_by_id(game_id, player_id, db)


# Abandonar juego
@player_router.post("/players/{player_id}/leave")
async def get_player_by_id(game_id: int, player_id: int, db: Session = Depends(get_db), repo: PlayerRepository = Depends()):
    repo.leave_game(game_id, player_id, db)

    message = {"type": "PLAYER_LIST_UPDATE"}
    await manager.broadcast(message)

    return message
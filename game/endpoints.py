import random
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database.db import get_db
from .models import Game
from .schemas import GameCreate, GameInDB
from player.models import Player
from player.schemas import PlayerCreateMatch, PlayerInDB
from gameState.models import GameState, StateEnum
from gameState.schemas import GameStateInDB
from .game_repository import GameRepository

game_router = APIRouter()

# Crear partida
@game_router.post("/games", status_code=status.HTTP_201_CREATED)
async def create_game(game: GameCreate, 
                      player: PlayerCreateMatch, 
                      db: Session = Depends(get_db), 
                      repo: GameRepository = Depends()):
    
    return repo.create_game(game, player, db)
    

# Obtener todas las partidas
@game_router.get("/games")
async def get_games(db: Session = Depends(get_db), repo: GameRepository = Depends()):
    return repo.get_games(db)


# Obtener partida segun id
@game_router.get("/games/{game_id}")
async def get_game_by_id(game_id: int, db: Session = Depends(get_db), repo: GameRepository = Depends()):
    return repo.get_game_by_id(game_id, db)
import random
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database.db import get_db
from .models import Game
from .schemas import GameCreate, GameInDB
from player.models import Player, turnEnum
from player.schemas import PlayerCreateMatch, PlayerInDB
from player.player_repository import PlayerRepository
from gameState.models import GameState, StateEnum
from gameState.schemas import GameStateInDB
from .game_repository import GameRepository
from board.board_repository import BoardRepository
from connection_manager import manager

game_router = APIRouter(
    tags=['Game']
)

# Crear partida
@game_router.post("/games", status_code=status.HTTP_201_CREATED)
async def create_game(game: GameCreate, 
                      player: PlayerCreateMatch, 
                      db: Session = Depends(get_db), 
                      repo: GameRepository = Depends()):
    
        res = repo.create_game(game, player, db)
        games_list_update = {
            "type": "GAMES_LIST_UPDATE"
        }
        await manager.broadcast(games_list_update)

        return res    

# Obtener todas las partidas
@game_router.get("/games")
async def get_games(page: int = Query(1, ge=1, description = "Numero de pagina, empieza en 1"),
                    limit: int = Query(5, ge=1, descripton = "Limita el numero de partidas mostradas por pagina"),
                    db: Session = Depends(get_db), 
                    repo: GameRepository = Depends()):

    # Calculo el offset segun la pagina y el limite
    offset = (page - 1) * limit

    return repo.get_games(db, offset=offset, limit=limit)

# Obtener partida segun id
@game_router.get("/games/{game_id}")
async def get_game_by_id(game_id: int, db: Session = Depends(get_db), repo: GameRepository = Depends()):
    return repo.get_game_by_id(game_id, db)


# Obtener ganador
@game_router.get("/games/{game_id}/winner")
async def get_game_winner(game_id: int, db: Session = Depends(get_db), repo: GameRepository = Depends()):
    return repo.get_game_winner(game_id, db)

@game_router.get("/games/{game_id}/board")
async def get_board(game_id: int, db: Session = Depends(get_db), repo: BoardRepository = Depends()):
    return repo.get_configured_board(game_id, db)
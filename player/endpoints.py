from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from .player_repository import PlayerRepository
from .schemas import PlayerJoinRequest
from game.game_repository import GameRepository
from connection_manager import manager
from game.utils import GameUtils

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
async def leave_game(game_id: int, player_id: int, db: Session = Depends(get_db), repo: PlayerRepository = Depends()):
    await repo.leave_game(game_id, player_id, db)

    message = {
            "type":f"{game_id}:GAME_INFO_UPDATE"
        }
    await manager.broadcast(message)
    
    message = {
            "type": "GAMES_LIST_UPDATE"
    }
    await manager.broadcast(message)


    return message

@player_router.post("/players/join/{game_id}", status_code= status.HTTP_201_CREATED)
async def join_game(game_id: int, 
                    player_name: PlayerJoinRequest, 
                    db: Session = Depends(get_db), 
                    repo: PlayerRepository = Depends(), 
                    game_repo: GameRepository = Depends()):
    
    game_utils = GameUtils(game_repo)
    #Verificar que no se supere el maximo de jugadores
    game = game_repo.get_game_by_id(game_id, db)
    players_in_game = game_utils.count_players_in_game(game_id, db)
    
    if game.get('max_players') == players_in_game:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="The game is full.")
    
    res = repo.create_player(game_id, player_name.player_name, db)
    
    player_list_update = {
            "type":f"{game_id}:GAME_INFO_UPDATE"
        }
    await manager.broadcast(player_list_update)
    
    player_list_update = {
            "type": "GAMES_LIST_UPDATE"
    }
    await manager.broadcast(player_list_update)

        
    return res
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from .player_repository import PlayerRepository
from .schemas import PlayerJoinRequest
from game.game_repository import GameRepository
from gameState.game_state_repository import GameStateRepository
from gameState.models import StateEnum
from movementCards.movement_cards_repository import MovementCardsRepository

from connection_manager import manager

from game.game_logic import get_game_logic, GameLogic
from partial_movement.partial_movement_logic import PartialMovementLogic, get_partial_movement_logic

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
async def leave_game(game_id: int, player_id: int, db: Session = Depends(get_db), 
                     repo: PlayerRepository = Depends(), game_logic: GameLogic = Depends(get_game_logic),
                     game_repo: GameRepository = Depends(), game_state_repo: GameStateRepository = Depends(),
                     partial_movement_logic: PartialMovementLogic = Depends(get_partial_movement_logic),
                     mov_card_repo: MovementCardsRepository = Depends()):
    
    #Revertir movimientos parciales si es necesario
    reverted_movements = partial_movement_logic.revert_partial_movements(game_id, player_id,db)

    # aviso que se fue el owner
    player = repo.get_player_by_id(game_id, player_id, db)
    game_state = game_state_repo.get_game_state_by_id(game_id, db)
    if player.host and game_state.state == StateEnum.WAITING:
        message = {
            "type": "OWNER_LEFT"
        }
        await manager.broadcast(message)

    response = await repo.leave_game(game_id, player_id, game_logic, game_repo, game_state_repo, mov_card_repo, db)

    if game_state.state == StateEnum.PLAYING:
        #Si se cambia el turno del jugador actual porque este decidio abandonar la partida
        if response.get("changed_turn"):
            message = {
                "type":f"{game_id}:NEXT_TURN"
            }
            await manager.broadcast(message)
        
        #Notificamos nuevo tablero
        message = {
                "type": f"{game_id}:MOVEMENT_UPDATE"
            }
        await manager.broadcast(message)
    
    message = {
            "type":f"{game_id}:GAME_INFO_UPDATE"
        }
    await manager.broadcast(message)
    
    message = {
            "type": "GAMES_LIST_UPDATE"
    }
    await manager.broadcast(message)


    return {"reverted_movements": reverted_movements}

@player_router.post("/players/join/{game_id}", status_code= status.HTTP_201_CREATED)
async def join_game(game_id: int, 
                    player_name: PlayerJoinRequest, 
                    db: Session = Depends(get_db), 
                    repo: PlayerRepository = Depends(), 
                    game_repo: GameRepository = Depends(),
                    game_logic: GameLogic = Depends(get_game_logic)
                    ):

    #Verificar que no se supere el maximo de jugadores
    game = game_repo.get_game_by_id(game_id, db)
    players_in_game = game_repo.count_players_in_game(game_id, db)
    
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
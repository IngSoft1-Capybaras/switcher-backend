from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db

from gameState.models import  StateEnum

from .game_state_repository import GameStateRepository
from player.player_repository import PlayerRepository
from board.board_repository import BoardRepository
from movementCards.movement_cards_repository import MovementCardsRepository
from figureCards.figure_cards_repository import FigureCardsRepository

from player.utils import PlayerUtils, get_player_utils
from player.player_repository import PlayerRepository
from movementCards.utils import MovementCardUtils, get_mov_cards_utils
from figureCards.utils import FigureCardUtils, get_fig_cards_utils
from connection_manager import manager


game_state_router = APIRouter(
    prefix= "/game_state",
    tags=['GameStatus']
)

@game_state_router.patch("/{game_id}/finish_turn", status_code= status.HTTP_200_OK)
async def finish_turn(game_id: int, game_state_repo:  GameStateRepository = Depends(), db: Session = Depends(get_db)):
    
    next_player_id = game_state_repo.get_next_player_id(game_id, db)
    
    game_state_repo.update_current_player(game_id, next_player_id, db)
    
    #notificar a los jugadores
    message = {
            "type":f"{game_id}:NEXT_TURN"
        }
    await manager.broadcast(message)
    
    return {"message": "Current player successfully updated"}

@game_state_router.patch("/start/{game_id}", status_code=status.HTTP_200_OK)
async def start_game(
    game_id: int,
    db: Session = Depends(get_db),
    player_repo: PlayerRepository = Depends(),
    game_state_repo: GameStateRepository = Depends(),
    player_utils: PlayerUtils = Depends(get_player_utils),
    board_repo: BoardRepository = Depends(),
    mov_cards_utils: MovementCardUtils = Depends(get_mov_cards_utils),
    fig_cards_utils: FigureCardUtils = Depends(get_fig_cards_utils)
):
    
    #Verificar que existan jugadores en la partida
    players = player_repo.get_players_in_game(game_id, db)
    
    # Asignar turnos aleatoriamente cada jugador y obtener primer jugador
    first_player_id = player_utils.assign_random_turns(players,db)
    
    #Crear tablero
    board_creation_result = board_repo.configure_board(game_id, db)
    
    #Crear Mazo Movimientos y asignar 3 a cada jugador
    mov_deck_creation = mov_cards_utils.create_mov_deck(game_id, db)

    
    #Crear Mazo Figuras para cada jugador
    fig_deck_creation = fig_cards_utils.create_fig_deck(db, game_id)
    
    # Cambiar estado de la partida
    game_state_repo.update_game_state(game_id, StateEnum.PLAYING, db)
    game_state_repo.update_current_player(game_id, first_player_id, db)
    
    #notificar a los jugadores
    message = {
            "type":f"{game_id}:GAME_STARTED"
        }
    await manager.broadcast(message)

    return {"message": "Game status updated, ur playing!"}



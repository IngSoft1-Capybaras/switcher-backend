from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from database.db import get_db

from gameState.models import  StateEnum

from player.models import Player, turnEnum
from game.models import Game
from gameState.models import GameState, StateEnum
from gameState.schemas import GameStateInDB

from .game_state_repository import GameStateRepository
from player.player_repository import PlayerRepository
from board.board_repository import BoardRepository
from movementCards.movement_cards_repository import MovementCardsRepository
from figureCards.figure_cards_repository import FigureCardsRepository

from player.utils import PlayerUtils, get_player_utils
from player.player_repository import PlayerRepository
from movementCards.movement_cards_logic import MovementCardLogic, get_mov_cards_logic
from figureCards.figure_cards_logic import FigureCardsLogic, get_fig_cards_logic
from connection_manager import manager


game_state_router = APIRouter(
    prefix= "/game_state",
    tags=['GameStatus']
)

@game_state_router.get("/{game_id}/current_turn", status_code=status.HTTP_200_OK)
async def get_current_player(game_id: int, db: Session = Depends(get_db)):
    game_state_repo =  GameStateRepository()
    
    return game_state_repo.get_current_player(game_id, db)

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
    mov_cards_logic: MovementCardLogic = Depends(get_mov_cards_logic),
    fig_cards_logic: FigureCardsLogic = Depends(get_fig_cards_logic)
):
    
    #Verificar que existan jugadores en la partida
    players = player_repo.get_players_in_game(game_id, db)
    
    # Asignar turnos aleatoriamente cada jugador y obtener primer jugador
    first_player_id = player_utils.assign_random_turns(players,db)
    
    #Crear tablero
    board_creation_result = board_repo.configure_board(game_id, db)
    
    #Crear Mazo Movimientos y asignar 3 a cada jugador
    mov_deck_creation = mov_cards_logic.create_mov_deck(game_id, db)

    
    #Crear Mazo Figuras para cada jugador
    fig_deck_creation = fig_cards_logic.create_fig_deck(db, game_id)
    
    # Cambiar estado de la partida
    game_state_repo.update_game_state(game_id, StateEnum.PLAYING, db)
    game_state_repo.update_current_player(game_id, first_player_id, db)
    
    #notificar a los jugadores
    message = {
            "type":f"{game_id}:GAME_STARTED"
        }
    await manager.broadcast(message)

    return {"message": "Game status updated, ur playing!"}

@game_state_router.get("/{game_id}")
async def get_game_state(game_id: int, db: Session = Depends(get_db), repo: GameStateRepository = Depends()):
    return repo.get_game_state_by_id(game_id, db)

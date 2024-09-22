import random
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db

from player.models import Player, turnEnum
from game.models import Game
from gameState.models import GameState, StateEnum

from .game_state_repo import GameStateRepository
from player.player_repository import PlayerRepository
from board.board_repository import BoardRepository
from movementCards.movement_cards_repository import MovementCardsRepository
from figureCards.figure_card_repository import FigureCardRepository

from player.utils import PlayerUtils
from movementCards.utils import MovementCardUtils
from figureCards.utils import FigureCardUtils


game_state_router = APIRouter(
    prefix= "/game_state",
    tags=['GameStatus']
)


@game_state_router.patch("/start/{game_id}", status_code=status.HTTP_200_OK)
async def start_game(game_id: int, db: Session = Depends(get_db)):
    player_repo = PlayerRepository()
    game_state_repo =  GameStateRepository()
    player_utils = PlayerUtils(player_repo)
    board_repo = BoardRepository()
    mov_cards_utils = MovementCardUtils(MovementCardsRepository())
    fig_cards_utils = FigureCardUtils(FigureCardRepository(), player_repo)
    
    #Verificar que existan jugadores en la partida
    players = player_repo.get_players_in_game(game_id)
    
    # Asignar turnos aleatoriamente cada jugador y obtener primer jugador
    first_player_id = player_utils.assign_random_turns(players,db)
    
    #Crear tablero
    board_creation_result = board_repo.configure_board(game_id)
    if "error" in board_creation_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=board_creation_result["error"])
    
    #Crear Mazo Movimientos
    mov_deck_creation = mov_cards_utils.create_mov_deck(db, game_id)
    if "error" in mov_deck_creation:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to create movement deck")
    
    #Crear Mazo Figuras para cada jugador
    fig_deck_creation = fig_cards_utils.create_fig_deck(db, game_id)
    if "error" in fig_deck_creation:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to create figure deck")
    
    # Cambiar estado de la partida
    game_state_repo.update_game_state(game_id, StateEnum.PLAYING)
    game_state_repo.update_current_player(game_id, first_player_id)
    
    return {"message": "Game status updated, ur playing!"}

#NO SUBIR A DEV , ENDPOINT DE FACU
@game_state_router.get("/current-player/{gameId}", status_code=status.HTTP_200_OK)
async def getCurrentPlayer(gameId: int, db: Session = Depends(get_db)):
    # Buscamos GameState con el id
    gameStateInstance = db.query(GameState).filter(GameState.idGame == gameId).first()
    if not gameStateInstance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Game State found for game with id {gameId}")
    
    # Obtenemos el id de quien esta jugando
    currentPlayer = gameStateInstance.currentPlayer
    if not currentPlayer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No current player found for game with id {gameId}")
    
    # Return the current player's info
    return {
        "id": currentPlayer
    }
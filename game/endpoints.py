import random
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from .models import Game
from .schemas import GameCreate, GameInDB
from player.models import Player, turnEnum
from player.schemas import PlayerCreateMatch, PlayerInDB
from gameState.models import GameState, StateEnum
from gameState.schemas import GameStateInDB
from board.utils import create_board

game_router = APIRouter(
    tags=['Game']
)

# Crear partida
@game_router.post("/games", status_code=status.HTTP_201_CREATED)
async def create_game(game: GameCreate, player: PlayerCreateMatch, db: Session = Depends(get_db)):
    game_instance = Game(**game.model_dump())
    db.add(game_instance)
    db.commit()
    db.refresh(game_instance)

    game_status_instance = GameState(idGame=game_instance.id ,state=StateEnum.WAITING)
    db.add(game_status_instance)
    db.commit()
    db.refresh(game_status_instance)

    player_instance = Player(
        game_id=game_instance.id, 
        name=player.name,
        game_state_id=game_status_instance.id,
        turn="PRIMERO",
        host=True
    )
    db.add(player_instance)
    db.commit()
    db.refresh(player_instance)

    return {
    "game": GameInDB.model_validate(game_instance),
    "player": PlayerInDB.model_validate(player_instance),
    "gameState": GameStateInDB.model_validate(game_status_instance)
}
    
    
@game_router.patch("/game/start/{game_id}", status_code=status.HTTP_200_OK)
async def start_game(game_id: int, db: Session = Depends(get_db)):
    # Obtener jugadores de la partida con id
    players = db.query(Player).filter(Player.game_id == game_id).all()
    if not players:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No players for game of id {game_id}")
    
    # FALTA: chequear min cantidad de participantes
    
    # Asignar turnos aleatoriamente cada jugador
    randomTurns = random.sample(range(1, len(players) + 1), len(players))
    turnMapping = {1: turnEnum.PRIMERO, 2: turnEnum.SEGUNDO, 3: turnEnum.TERCERO, 4: turnEnum.CUARTO}
    
    firstPlayer = None
    
    for player, turn in zip(players, randomTurns):
        player.turn = turnMapping[turn]
        
        if turn == 1:
            firstPlayer = player
            
    
    #Crear tablero
    board_creation_result = create_board(db, game_id)
    if "error" in board_creation_result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=board_creation_result["error"])
    
    
    # Cambiar estado de la partida
    gameInstance = db.query(Game).filter(Game.id == game_id).first()
    if not gameInstance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No game with id {game_id}")
    
    # El estado de juego debe existir con estado en waiting
    gameStateInstance = db.query(GameState).filter(GameState.idGame == game_id).first()
    if not gameStateInstance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Game State match found for game of id {game_id}")
    
    gameStateInstance.currentPlayer = firstPlayer.id
    gameStateInstance.state = StateEnum.PLAYING
    
    db.commit()
    
    return {"message": "Game status updated, ur playing!"}

@game_router.get("/game/current-player/{gameId}", status_code=status.HTTP_200_OK)
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
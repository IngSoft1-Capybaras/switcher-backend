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

game_router = APIRouter()

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
        id=random.randint(1, 1000),
        game_id=game_instance.id, 
        name=player.name,
        game_state_id=game_status_instance.id,
        turn="primero",
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
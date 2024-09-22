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

    game_status_instance = GameState(game_id=game_instance.id ,state=StateEnum.WAITING)
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

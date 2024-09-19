from fastapi import APIRouter, status
from pony.orm import db_session, select
# from ..database import db 
from .models import Game
from .schemas import GameCreate
from player.models import Player
from player.schemas import PlayerCreateMatch
from gameState.models import GameState
from gameState.schemas import StateEnum



game_router = APIRouter()

# Crear partida
@game_router.post("/games", status_code=status.HTTP_201_CREATED)
async def create_game(game: GameCreate, player: PlayerCreateMatch):
    with db_session:
        game_instance = Game(**game.model_dump())
        game_status_instance = GameState(idGame=game_instance ,state=StateEnum.WAITING)
        player_instance = Player(idGame=game_instance, **player.model_dump(), idGameStatus=game_instance.gameState, figureCards=[], movementCards=[])
        return {
            "game": game_instance.to_dict(),
            "player": player_instance.to_dict(),
            "gameState": game_status_instance.to_dict()
        }
    
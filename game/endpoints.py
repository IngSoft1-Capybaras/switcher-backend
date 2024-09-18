from fastapi import APIRouter, status
from pony.orm import db_session, select
# from ..database import db 
from .models import Game
from .schemas import GameInDB


game_router = APIRouter()

# Obtener todas las partidas
@game_router.get("/games")
async def get_games():
    with db_session:
        games = Game.select()
        result = [GameInDB.from_orm(g) for g in games]
        return result


# Obtener partida segun id
@game_router.get("/games/{game_id}")
async def get_games_by_id(game_id: int):
    with db_session:
        games = Game.select()
        result = [GameInDB.from_orm(g) for g in games if g.id == game_id]
        return result[0]

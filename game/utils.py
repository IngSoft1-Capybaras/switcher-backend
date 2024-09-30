from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from sqlalchemy.exc import NoResultFound
from .models import Game
from game.game_repository import GameRepository
from gameState.game_state_repository import GameStateRepository
from gameState.models import StateEnum
from player.models import Player
from connection_manager import manager


def get_game_utils(game_repo: GameRepository = Depends()):
    return GameUtils(game_repo)
class GameUtils:
    def __init__(self, game_repository: GameRepository):
        self.game_repository = game_repository

    def count_players_in_game(self, game_id: int, db: Session) -> int:
        try:
            game = db.query(Game).filter(Game.id == game_id).one()
            
        except NoResultFound:
            raise HTTPException(status_code = 404, detail = "Game not found")
        
        player_count = game.players_count()
        return player_count


    async def check_win_condition(self, game: Game, db: Session):
        # chequeo si queda solo uno
        
        players_left = game.players
        
        if len(players_left) == 1:
            await self.handle_win(game.id, players_left[0], db)
            return True
        
        return False
        # aca irian el resto de las condiciones que se veran en otros sprints


    async def handle_win(self, game_id: int, last_player: Player, db: Session):
        game_state_repository = GameStateRepository()

        # actualizo partida a finalizada
        game_state_repository.update_game_state(game_id, StateEnum.FINISHED, db)
        
        # asigno al ultimo jugador como ganador
        last_player.winner = True
        db.add(last_player)
        db.commit()
        
        player_update = {
                "type": "PLAYER_WINNER",
                "game_id": game_id,
                "winner_id": last_player.id,
                "winner_name": last_player.name
        }

        await manager.broadcast(player_update)
        

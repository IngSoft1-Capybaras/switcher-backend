from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from sqlalchemy.exc import NoResultFound
from .models import Game
from game.game_repository import GameRepository
from gameState.game_state_repository import GameStateRepository
from gameState.models import StateEnum
from player.models import Player
from player.player_repository import PlayerRepository
from connection_manager import manager


def get_game_logic(game_repo: GameRepository = Depends()):
    return GameLogic(game_repo)

class GameLogic:
    def __init__(self, game_repository: GameRepository):
        self.game_repository = game_repository


    async def check_win_condition(self, game: Game, db: Session):
        # chequeo si queda solo uno
        
        players_left = game.players
        
        if len(players_left) == 1:
            await self.handle_win(game.id, players_left[0], db)
            return True
        
        return False
        # aca irian el resto de las condiciones que se veran en otros sprints


    async def handle_win(self, game_id: int, last_player: Player, db: Session, player_repo: PlayerRepository = Depends()):
        game_state_repository = GameStateRepository()

        # actualizo partida a finalizada
        game_state_repository.update_game_state(game_id, StateEnum.FINISHED, db)
        
        # asigno al ultimo jugador como ganador
        player_repo.assign_winner_of_game(last_player, db)
        
        player_update = {
                "type": "PLAYER_WINNER",
                "game_id": game_id,
                "winner_id": last_player.id,
                "winner_name": last_player.name
        }

        await manager.broadcast(player_update)
        

from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from sqlalchemy.exc import NoResultFound
from .models import Game
from game.game_repository import GameRepository, get_game_repository
from gameState.game_state_repository import GameStateRepository
from gameState.models import StateEnum
from player.models import Player
from player.player_repository import PlayerRepository
from figureCards.figure_cards_repository import FigureCardsRepository, get_figure_cards_repository
from connection_manager import manager


def get_game_logic(game_repo: GameRepository = Depends(get_game_repository), 
                   game_state_repo : GameStateRepository = Depends(), player_repo : PlayerRepository = Depends(), 
                   figure_cards_repo: FigureCardsRepository = Depends(get_figure_cards_repository)):
    
    return GameLogic(game_repo,game_state_repo, player_repo, figure_cards_repo)

class GameLogic:
    def __init__(self, game_repository: GameRepository, game_state_repository: GameStateRepository, 
                 player_repository: PlayerRepository, figure_cards_repo: FigureCardsRepository):
        self.game_repository = game_repository
        self.game_state_repo = game_state_repository
        self.player_repo = player_repository
        self.figure_cards_repo = figure_cards_repo


    async def check_win_condition(self, game_id: int, db: Session):

        # chequeo si queda solo uno
        players_left = self.player_repo.get_players_in_game(game_id, db)
        
        if len(players_left) == 1:
            await self.handle_win(game_id, players_left[0].id, db)
            return True
  
        return False
    

        # aca irian el resto de las condiciones que se veran en otros sprints


    async def handle_win(self, game_id: int, winner_player_id: int, db: Session):
        
        winner_player = self.player_repo.get_player_by_id(game_id, winner_player_id, db)

        # actualizo partida a finalizada
        self.game_state_repo.update_game_state(game_id, StateEnum.FINISHED, db)
        
        # asigno al ultimo jugador como ganador
        self.player_repo.assign_winner_of_game(game_id, winner_player_id, db)
        
        player_update = {
                "type": "PLAYER_WINNER",
                "game_id": game_id,
                "winner_id": winner_player.id,
                "winner_name": winner_player.name
        }

        await manager.broadcast(player_update)
        
        # borro el juego
        self.game_repository.delete_game(game_id, db)
        
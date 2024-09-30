from player.models import Player
from game.models import Game
from game.game_repository import GameRepository
from sqlalchemy.orm import Session
from .models import GameState, StateEnum
from .game_state_repository import GameStateRepository
from fastapi import HTTPException, status

class GameStateUtils:
    def __init__(
        self, game_repo: GameRepository, game_state_repo: GameStateRepository
    ):
        self.game_repo = game_repo
        self.game_state_repo = game_state_repo
    
    
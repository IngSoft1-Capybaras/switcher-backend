from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from fastapi import Depends, HTTPException
from .models import Player, turnEnum
from .schemas import PlayerInDB
from database.db import get_db

class PlayerRepository:
    
    def get_player_by_id(self, game_id: int, player_id: int, db: Session = Depends(get_db)) -> PlayerInDB:            
        try:
            player_in_db = db.query(Player).filter(Player.id == player_id, 
                                                Player.has(game_id=game_id)).one()
        
        except NoResultFound:
            raise HTTPException(status_code = 404, detail = "The is no such player")
        
        
        return PlayerInDB.model_validate(player_in_db)

    
    def get_players_in_game(self, game_id: int, db: Session = Depends(get_db)) -> dict:
        
        players = db.query(Player).filter(Player.game_id == game_id).all()
        
        if not players:
            raise HTTPException(status_code = 404, detail = "Game not found")
        
        return [PlayerInDB.model_validate(player) for player in players]

    
    def assign_turn_player(self, game_id: int, player_id: int, turn: turnEnum, db: Session = Depends(get_db)):
        try:
            player = db.query(Player).filter(Player.id == player_id,
                                                  Player.has(game_id=game_id)).one()
        
        except NoResultFound:
            raise HTTPException(status_code = 404, detail = "There is no such player")

            
        player.turn = turn
            
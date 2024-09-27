from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from .models import GameState, StateEnum
from .schemas import GameStateInDB
from database.db import get_db
from player.models import Player, turnEnum


class GameStateRepository:
    
    def update_game_state(self, game_id: int, state: StateEnum, db : Session ):
        try:
            game_state_instance = db.query(GameState).filter(GameState.game_id == game_id).first()

            if not game_state_instance:
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game State not found"
            )
            game_state_instance.state = state
            db.commit()
        finally:
            db.close()
    
    def update_current_player(self, game_id: int, first_player_id: int, db : Session):
        
        try: 
            game_state_instance = db.query(GameState).filter(GameState.game_id == game_id).first()

            if not game_state_instance:
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game State not found"
                )

            game_state_instance.current_player = first_player_id
            db.commit()
        finally:
            db.close()
    
    def get_game_state_by_id(self, game_id: int, db : Session) -> GameStateInDB:
        try:
            
            game_state_in_db = db.query(GameState).filter(GameState.game_id == game_id).first()

            if not game_state_in_db:
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game State not found"
                )
        finally:
            db.close()
        
        return GameStateInDB.model_validate(game_state_in_db)


    def get_next_player_id(self, game_id: int, game_state_id: int, db : Session) -> int:
        
        try:
            game_state_instance = db.query(GameState).filter(GameState.game_id == game_id,
                                                             GameState.id == game_state_id).first()
            
            if not game_state_instance:
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game State not found"
                )
            current_player_id = game_state_instance.current_player
            
            players = db.query(Player).filter(Player.game_id == game_id).all()
        
            if not players:
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Players not found"
                )
            
            current_player = next((player for player in players if player.id == current_player_id), None)
            
            if not current_player:
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Current player not found"
                )
            
            current_turn = current_player.turn
            
            turn_order = [
                turnEnum.PRIMERO,
                turnEnum.SEGUNDO,
                turnEnum.TERCERO,
                turnEnum.CUARTO
            ]
            
            current_turn_index = turn_order.index(current_turn)
            next_turn = turn_order[(current_turn_index + 1) % len(turn_order)]
            
            next_player = next((player for player in players if player.turn == next_turn), None)
            
            if not next_player:
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Next player not found"
                )
            
            return next_player.id
            
            
        finally: 
            db.close()

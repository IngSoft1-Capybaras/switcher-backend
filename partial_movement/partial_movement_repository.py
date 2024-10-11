from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from .models import PartialMovements

from board.schemas import BoardPosition
from game.models import Game
from player.models import Player
from movementCards.models import MovementCard



class PartialMovementRepository:
    
    def create_partial_movement(self, game_id: int, player_id: int, card_id: int, pos_from: BoardPosition , pos_to: BoardPosition, db: Session):
        # Verificamos exist el juego
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
        
        # verificamos si existe el jugador en el juego
        player = db.query(Player).filter(Player.id == player_id, Player.game_id == game_id).first()
        if not player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found in the specified game")
        
        # cerificamos si existe la carta en la mano del jugador en el juego
        card = db.query(MovementCard).filter(MovementCard.id == card_id, 
                                             MovementCard.player_id == player_id, 
                                             MovementCard.game_id == game_id
                                            ).first()
        if not card:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found for the specified player and game")
        
        partial_movement = PartialMovements(
            game_id=game_id,
            player_id=player_id,
            mov_card_id=card_id,
            pos_from_x=pos_from.pos[0],
            pos_from_y=pos_from.pos[1],
            pos_to_x=pos_to.pos[0],
            pos_to_y=pos_to.pos[1]
        )
        
        db.add(partial_movement)
        db.commit()
        
        
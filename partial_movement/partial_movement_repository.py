from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from .models import PartialMovements

from board.schemas import BoardPosition



class PartialMovementRepository:
    
    def create_partial_movement(self, game_id: int, player_id: int, card_id: int, pos_from: BoardPosition , pos_to: BoardPosition, db: Session):
        partial_movement = PartialMovements(
            game_id=game_id,
            player_id=player_id,
            mov_card_id=card_id,
            pos_from_x=pos_from.x,
            pos_from_y=pos_from.y,
            pos_to_x=pos_to.x,
            pos_to_y=pos_to.y
        )
        
        try: 
            db.add(partial_movement)
            db.commit()
        except IntegrityError:
            #si alguna de las FK falla (por ejemplo no existen en la DB, enviamos un mensaje de error)
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Integrity error while creating partial movement: check foreign key values")
        
        
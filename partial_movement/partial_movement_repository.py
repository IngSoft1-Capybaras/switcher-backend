from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from sqlalchemy.exc import NoResultFound
import random
from sqlalchemy import select

from .models import PartialMovements

from board.schemas import BoardPosition
from board.board_repository import BoardRepository
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

    # se comporta como un pop de un stack    
    def undo_movement(self, db: Session) -> PartialMovements:
        # busco la ultima fila de la tabla partial movements
        last_parcial_movement = db.execute(
            select(PartialMovements).order_by(PartialMovements.id.desc())
            ).scalar()
        
        if last_parcial_movement is None:
            raise HTTPException(status_code=404, detail="There is no partial movement to undo")

        # elimino la fila
        db.delete(last_parcial_movement)

        db.commit()

        # devuelvo el movimiento eliminado
        return last_parcial_movement


def get_partial_movement_repository(partial_movement_repo: PartialMovementRepository = Depends()) -> PartialMovementRepository:
    return partial_movement_repo

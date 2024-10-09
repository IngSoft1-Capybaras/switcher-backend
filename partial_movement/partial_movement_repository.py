import random
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import Depends, HTTPException
from partial_movement.models import PartialMovements


class PartialMovementRepository:

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

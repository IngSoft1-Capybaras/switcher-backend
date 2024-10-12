import pytest
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from partial_movement.models import PartialMovements
from partial_movement.partial_movement_repository import PartialMovementRepository
from fastapi import HTTPException

from database.db import engine

#Configuración de la sesión
Session = sessionmaker(bind=engine)


@pytest.fixture
def partial_movement_repo():
    return PartialMovementRepository()

@pytest.mark.integration_test
def test_undo_movement(partial_movement_repo: PartialMovementRepository, session):
    # agrego un movimiento parcial
    partial_mov = PartialMovements(
        pos_from_x = 0,
        pos_from_y = 0,
        pos_to_x = 1,
        pos_to_y = 1, 
        game_id = 1,
        player_id = 1,
        mov_card_id = 1
    )

    session.add(partial_mov)
    session.commit()
    
    N_partial_movement = session.query(PartialMovements).count()

    # agarro el ultimo por id
    last_partial_movement_in_db = session.query(PartialMovements).order_by(PartialMovements.id.desc()).first()

    partial_movement_deleted = partial_movement_repo.undo_movement(session)

    # me fijo que en efecto se haya borrado 
    assert N_partial_movement - 1 == session.query(PartialMovements).count() 
    assert last_partial_movement_in_db.id == partial_movement_deleted.id
    assert partial_mov.mov_card_id == partial_movement_deleted.mov_card_id


@pytest.mark.integration_test
def test_undo_inexistent_movement(partial_movement_repo: PartialMovementRepository, session):
    # me fijo que no haya nada
    # assert session.query(PartialMovementRepository).count() == 0
    
    with pytest.raises(HTTPException) as excinfo:
        partial_movement_repo.undo_movement(session)
    
    assert excinfo.value.status_code == 404
    assert "There is no partial movement to undo" in str(excinfo.value.detail)
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.db import get_db

from .movement_cards_repository import MovementCardsRepository, get_movement_cards_repository
from .movement_cards_logic import MovementCardLogic, get_mov_cards_logic

from board.schemas import BoardPosition
from partial_movement.partial_movement_repository import PartialMovementRepository

movement_cards_router = APIRouter(
    prefix= "/deck/movement",
    tags=['MovementCards']
)

# Obtener cartas de movimiento
@movement_cards_router.get("/{game_id}/{player_id}")
async def get_movement_cards(game_id: int, player_id: int, 
                             db: Session = Depends(get_db), 
                             repo: MovementCardsRepository = Depends(get_movement_cards_repository)):
    
    return repo.get_movement_cards(game_id, player_id, db)

# Obtener todas las cartas de movimiento
@movement_cards_router.get("/{game_id}/{player_id}/{card_id}")
async def get_movement_card_by_id(game_id: int, player_id: int, 
                                  card_id: int, db: Session = Depends(get_db), 
                                  repo: MovementCardsRepository = Depends(get_movement_cards_repository)):
    
    return repo.get_movement_card_by_id(game_id, player_id, card_id, db)

@movement_cards_router.post("/play_card", status_code = status.HTTP_201_CREATED)
async def play_movement_card(
                                game_id: int, 
                                player_id: int, 
                                card_id: int, 
                                pos_from: BoardPosition , 
                                pos_to: BoardPosition, 
                                mov_cards_logic: MovementCardLogic = Depends(get_mov_cards_logic), 
                                partial_mov_repo: PartialMovementRepository = Depends() ,
                                mov_cards_repo: MovementCardsRepository = Depends(),
                                db: Session = Depends(get_db)
                            ):
    #validar movimiento
    mov_cards_logic.validate_movement(card_id, pos_from, pos_to)
    #si el movimiento no es valido se le debe avisar el problema al jugador (?) 
    
    #si el movimiento es valido entonces lo registramos como un movimiento parcial
    partial_mov_repo.create_partial_movement(game_id, player_id, card_id, pos_from, pos_to, db)
    #registar carta de movimiento como parcialmente usada
    mov_cards_repo.mark_card_partially_used(card_id,db)
    #se realizan los cambios en el tablero
    
    #se avisa a los jugadores del nuevo tablero
    
    
    #Cambiar mensaje
    return {"message": "Play your cards right..."}
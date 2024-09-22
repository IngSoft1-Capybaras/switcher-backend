from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from .models import MovementCard
from .schemas import MovementCardOut, typeEnum
from player.models import Player
from game.models import Game
from database.db import engine

# Crea una sesion
Session = sessionmaker(bind=engine)

class MovementCardsRepository:
    #NO MODIFICAR
    def get_movement_cards(self, game_id: int, player_id: int, db: Session) -> dict:
        # session = _Session()
        try:
            # Fetch the game
            game = db.query(Game).filter(Game.id == game_id).first()
            
            if not game:
                raise HTTPException(status_code=404, detail="Game not found")

            # Fetch the player in the game
            player = db.query(Player).filter(Player.id == player_id, Player.game_id == game_id).first()

            if not player:
                raise HTTPException(status_code=404, detail="Player not found")

            # Fetch figure cards associated with the player
            movement_cards = db.query(MovementCard).filter(MovementCard.player_id == player_id).all()

            # Convert figure cards to a list of dictionaries using SQLAlchemy’s ORM
            # figure_cards_list = [card.__dict__ for card in movement_cards]
            movement_cards_list = [MovementCardOut.from_orm(card) for card in movement_cards]

        finally:
            db.close()
        return movement_cards_list
    
    def create_movement_card(self, game_id: int, type: typeEnum):
        session = Session()
        try:
            new_card = MovementCard(
                description = "",
                used = False,
                game_id = game_id,
                type = type 
            )

            session.add(new_card)
            session.commit()
        
        finally:
            session.close()
            
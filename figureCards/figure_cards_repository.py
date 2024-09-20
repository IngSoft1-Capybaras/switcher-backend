from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPE
from sqlalchemy.exc import NoResultFound
from .models import FigureCard
from .schemas import FigureCardSchema
from player.models import Player
from game.models import Game
from typing import List
from database.db import engine, Base, get_db

# Crea una sesion
# _Session = sessionmaker(bind=engine)

class FigureCardsRepository:

    def get_figure_cards(self, game_id: int, player_id: int, db: Session = Depends(get_db)) -> dict:
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
            figure_cards = db.query(FigureCard).filter(FigureCard.player_id == player_id).all()

            # Convert figure cards to a list of dictionaries using SQLAlchemy’s ORM
            # figure_cards_list = [card.__dict__ for card in figure_cards]
            figure_cards_list = [FigureCardSchema.from_orm(card) for card in figure_cards]

        finally:
            Session.close()
        return figure_cards_list
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from .models import FigureCard, typeEnum
from .schemas import FigureCardSchema


class FigureCardsRepository:

    def get_figure_cards(self, game_id: int, player_id: int, db : Session) -> dict:
        
        try:
            # Fetch figure cards associated with the player and game
            figure_cards = db.query(FigureCard).filter(FigureCard.player_id == player_id,
                                                       FigureCard.player.has(game_id=game_id)).all()

            if not figure_cards:
                raise HTTPException(status_code=404, detail="There no figure cards associated with this game and player")

            # Convert figure cards to a list of dictionaries using SQLAlchemy’s ORM
            # figure_cards_list = [card.__dict__ for card in figure_cards]
            figure_cards_list = [FigureCardSchema.from_orm(card) for card in figure_cards]

        finally:
            db.close()
        return figure_cards_list
    
    def get_figure_card_by_id(self, game_id: int, player_id: int, card_id: int, db : Session) -> FigureCardSchema:

        try:
            # Fetch the specific figure card by its id, player_id and game_id
            try:
                figure_card = db.query(FigureCard).filter(FigureCard.id == card_id, 
                                                          FigureCard.player_id == player_id,
                                                          FigureCard.player.has(game_id=game_id)).one()
            except NoResultFound:
                raise HTTPException(status_code=404, detail="Figure card not found")

            # Convert the figure card to a schema
            figure_card_schema = FigureCardSchema.from_orm(figure_card)

        finally:
            db.close()
        return figure_card_schema
    
    def create_figure_card(self, player_id: int, game_id: int, figure: typeEnum, db : Session):

        try:
            new_card = FigureCard(
                type=figure,
                show=False,
                game_id= game_id,
                player_id=player_id
            )
            db.add(new_card)
            db.commit()
        finally:
            db.close()

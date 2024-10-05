from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from .models import FigureCard, typeEnum
from .schemas import FigureCardSchema


class FigureCardsRepository:

    def get_figure_cards(self, game_id: int, player_id: int, db : Session) -> list:
        
        # busco las figure cards asociadas a game_id y player_id
        figure_cards = db.query(FigureCard).filter(FigureCard.player_id == player_id,
                                                    FigureCard.player.has(game_id=game_id)).all()

        if not figure_cards:
            raise HTTPException(status_code=404, detail="There no figure cards associated with this game and player")

        # convierto cada elemento en figure_cards a su schema
        figure_cards_list = [FigureCardSchema.model_validate(card) for card in figure_cards]

        return figure_cards_list
    
    def get_figure_card_by_id(self, game_id: int, player_id: int, card_id: int, db : Session) -> FigureCardSchema:
        # busco una figura card especifica segun game_id, player_id y card_id
        try:
            figure_card = db.query(FigureCard).filter(FigureCard.id == card_id, 
                                                        FigureCard.player_id == player_id,
                                                        FigureCard.player.has(game_id=game_id)).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Figure card not found")

        # convierto la figure card a su schema
        figure_card_schema = FigureCardSchema.model_validate(figure_card)

        return figure_card_schema
    
    def create_figure_card(self, player_id: int, game_id: int, figure: typeEnum, show: bool, db: Session):
        new_card = FigureCard(
            type=figure,
            show=show,
            game_id= game_id,
            player_id=player_id
        )
        db.add(new_card)
        db.commit()


def get_figure_cards_repository(figure_cards_repo: FigureCardsRepository = Depends()) -> FigureCardsRepository:
    return figure_cards_repo

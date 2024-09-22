from sqlalchemy.orm import sessionmaker
from .models import FigureCard
from .schemas import typeEnum
from database.db import engine


Session = sessionmaker(bind=engine)

class FigureCardRepository:

    def create_figure_card(self, player_id: int, game_id: int, figure: typeEnum):
        session = Session()
        try:
            new_card = FigureCard(
                type=figure,
                show=False,
                player_id=player_id
            )
            session.add(new_card)
            session.commit()
        finally:
            session.close()


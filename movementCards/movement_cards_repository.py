from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from .models import MovementCard
from .schemas import MovementCardSchema, typeEnum
from player.models import Player
from game.models import Game

import pdb

class MovementCardsRepository:

    def get_movement_cards(self, game_id: int, player_id: int, db : Session) -> list:
        # Fetch figure cards associated with the player and game
        movement_cards = db.query(MovementCard).filter(MovementCard.player_id == player_id,
                                                    MovementCard.player.has(game_id=game_id)).all()

        if not movement_cards:
            raise HTTPException(status_code=404, detail="There no movement cards associated with this game and player")

        # Convert movement cards to a list of schemas
        movement_cards_list = [MovementCardSchema.model_validate(card) for card in movement_cards]

        return movement_cards_list
    

    def get_movement_card_by_id(self, game_id: int, player_id: int, card_id: int, db : Session) -> MovementCardSchema:
        
        # Fetch the specific movement card by its id, player_id and game_id
        try:
            movement_card = db.query(MovementCard).filter(MovementCard.id == card_id, 
                                                        MovementCard.player_id == player_id,
                                                        MovementCard.player.has(game_id=game_id)).one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Movement card not found")

        # Convert the movement card to a schema
        movement_card_schema = MovementCardSchema.model_validate(movement_card)

        return movement_card_schema


    def create_movement_card(self, game_id: int, type: typeEnum, db : Session):
        new_card = MovementCard(
            description = "",
            used = False,
            game_id = game_id,
            type = type 
        )

        db.add(new_card)
        db.commit()


    def get_movement_deck(self, game_id: int, db : Session) -> list:
        # Fetch figure cards associated with the player and game
        movement_cards = db.query(MovementCard).filter(MovementCard.game_id == game_id,
                                                    MovementCard.player_id.is_(None)).all()

        if not movement_cards:
            raise HTTPException(status_code=404, detail="There no movement cards associated with this game")

        # Convert movement deck of cards to a list of schemas
        movement_cards_deck = [MovementCardSchema.model_validate(card) for card in movement_cards]

        return movement_cards_deck

    def assign_mov_card(self, mov_card_id: int, player_id: int, db : Session) -> list:
        # Fetch figure cards associated with the player and game
        mov_card = db.query(MovementCard).filter(MovementCard.id == mov_card_id).first()
            
        if not mov_card:
            raise HTTPException(status_code=400, detail="There no movement cards associated with this game")

        player = db.query(Player).filter(Player.id == player_id).first()

        if not mov_card:
            raise HTTPException(status_code=400, detail="no player with specified id")
        
        mov_card.player = player
        db.commit()

        return mov_card
    
    def grab_mov_cards(self, player_id: int, game_id: int,db: Session):
        try: 
            db.query(Game).filter(Game.id == game_id).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No game found")

        try: 
            db.query(Player).filter(Player.id == player_id, Player.game_id == game_id).one()
        except NoResultFound:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
        
        movement_cards = db.query(MovementCard).filter(
                                                        MovementCard.player_id == player_id,
                                                        MovementCard.game_id==game_id, 
                                                        MovementCard.used == False
                                                       ).all()
        
        cards_needed = 3 - len(movement_cards)
        
        if cards_needed > 0:
            #Obtengo cartas no asignadas a un jugador que no hayan sido usadas
            unassigned_cards = db.query(MovementCard).filter(
                                                                MovementCard.player_id.is_(None),
                                                                MovementCard.game_id == game_id,
                                                                MovementCard.used == False
                                                            ).limit(cards_needed).all()
            #Si no hay, volvemos a armar el mazo de mov con las cartas ya usadas
            if not unassigned_cards:
                self.reshuffle_movement_deck(game_id, db)
                #Obtengo las cartas necesarias para asignarle al jugador
                unassigned_cards = db.query(MovementCard).filter(
                                                                MovementCard.player_id.is_(None),
                                                                MovementCard.game_id == game_id,
                                                                MovementCard.used == False
                                                            ).limit(cards_needed).all()

            #Se las asigno al jugador    
            for card in unassigned_cards:
                card.player_id = player_id
            
            db.commit()

    def reshuffle_movement_deck(self, game_id : int, db: Session):
        used_cards = db.query(MovementCard).filter(
                                                    MovementCard.player_id.is_(None),
                                                    MovementCard.game_id == game_id,
                                                    MovementCard.used == True
                                                  ).all()

        if not used_cards:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No used cards available to reshuffle")        
        
        for card in used_cards:
            card.used = False
        
        db.commit()
        
        
        
def get_movement_cards_repository(movement_cards_repo: MovementCardsRepository = Depends()) -> MovementCardsRepository:
    return movement_cards_repo


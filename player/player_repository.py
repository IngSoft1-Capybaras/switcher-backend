from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from fastapi import Depends, HTTPException, status
from .models import Player, turnEnum
from .schemas import PlayerInDB
from game.models import Game
from game.game_repository import GameRepository
from game.utils import GameUtils
from gameState.models import GameState, StateEnum
from connection_manager import manager
from figureCards.models import FigureCard
from movementCards.models import MovementCard

class PlayerRepository:
    
    def get_player_by_id(self, game_id: int, player_id: int, db : Session) -> PlayerInDB:   
        
        try:
            player_in_db = db.query(Player).filter(Player.id == player_id, 
                                                Player.game_id == game_id).one()
        
        except NoResultFound:
            raise HTTPException(status_code = 404, detail = "The is no such player")
        
        
        return PlayerInDB.model_validate(player_in_db)

    
    def get_players_in_game(self, game_id: int, db : Session):
        try:
            game = db.query(Game).filter(Game.id == game_id).one()
        except NoResultFound :
            raise HTTPException(status_code=404, detail=f"Game {game_id} not found")
        
        players = db.query(Player).filter(Player.game_id == game_id).all()
        
        if not players:
            return []
        
        return [PlayerInDB.model_validate(player) for player in players]

    
    def assign_turn_player(self, game_id: int, player_id: int, turn: turnEnum, db : Session):
        try:
            player = db.query(Player).filter(Player.id == player_id,
                                            Player.game_id == game_id).one()
            player.turn = turn
            db.commit()
        except NoResultFound:
            raise HTTPException(status_code = 404, detail = "There is no such player")
        
        
    
    async def leave_game(self, game_id: int, player_id: int, db: Session):
        try:
            game = db.query(Game).filter(Game.id == game_id).one()
        except NoResultFound :
            raise HTTPException(status_code=404, detail="Game not found")
        
        try:
            game_state = db.query(GameState).filter(GameState.game_id == game_id).one()
        except NoResultFound :
            raise HTTPException(status_code=404, detail="Game state not found")
        
        if game_state.state == StateEnum.PLAYING:
            # descarto sus cartas de figura
            player_figure_cards = db.query(FigureCard).filter(FigureCard.player_id == player_id).all()
            
            if not player_figure_cards:
                raise HTTPException(status_code = 404, detail = f"Player {player_id} doesn't have any figure cards")
            

            for figure_card in player_figure_cards:
                db.delete(figure_card)

            # mando sus cartas de movimiento al mazo
            player_movement_cards = db.query(MovementCard).filter(MovementCard.player_id == player_id).all()
            
            if not player_movement_cards:
                raise HTTPException(status_code = 404, detail = f"Player {player_id} doesn't have any movement cards")
            
            for movement_card in player_movement_cards:
                movement_card.player_id = None
        

        # delete() devuelve la cantidad de filas afectadas por la operacion
        rows_deleted = db.query(Player).filter(Player.id == player_id, Player.game_id == game_id).delete()

        # si son cero las filas es porque no encontro el jugador
        if rows_deleted == 0:
            raise HTTPException(status_code = 404, detail = "There is no such player")

        db.commit()

        game_utils = GameUtils(GameRepository())

        if game_state.state == StateEnum.PLAYING:
            # chequeo la condicion de ganar por abandono
            await game_utils.check_win_condition(game, db)
        
        return {"message": "Player has successfully left the game"}
    
    def create_player(self, game_id: int, player_name: str, db : Session) -> int:
        try:
            game_status = db.query(GameState).filter(GameState.game_id == game_id).first()  
            game_status_id = game_status.id
        except NoResultFound:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="No game status for game")
        
        try:
            new_player = Player(
                name = player_name,
                game_id = game_id,
                game_state_id = game_status_id,
                host = False, 
                winner = False
            )

            db.add(new_player)
            
            db.flush()
            player_id = new_player.id
            
            db.commit()
        
        finally:
            db.close()
            
        return {"player_id": player_id}
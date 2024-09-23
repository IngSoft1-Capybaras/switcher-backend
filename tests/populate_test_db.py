import random
from database.db import SessionLocal, engine, init_db
from sqlalchemy.orm import sessionmaker
from board.models import Box, Board, ColorEnum
from figureCards.models import FigureCard, DifficultyEnum
from game.models import Game
from gameState.models import GameState, StateEnum
from movementCards.models import MovementCard
from player.models import Player, turnEnum

init_db()
Session = sessionmaker(bind=engine)

def create_game(name, min_players, max_players):
    session = Session()
    try:
        game = Game(name=name, minPlayers=min_players, maxPlayers=max_players)
        session.add(game)
        session.flush()
    finally:
        session.close()
    return game

def create_game_state(game, state):
    session = Session()
    try:
        game_state = GameState(state=state, game_id=game.id)
        session.add(game_state)
        session.flush()
    finally:
        session.close()
    return game_state

def create_player(name, game, game_state, turn, host):
    session = Session()
    try:
        player = Player(name=name, game_id=game.id, game_state_id=game_state.id, turn=turn, host=host)
        session.add(player)
        session.flush()
    finally:
        session.close()
    return player

def create_board(game):
    session = Session()
    try:
        board = Board(id_game=game.id)
        session.add(board)
        session.flush()
    finally:
        session.close()
    return board

def create_box(color, pos_x, pos_y, game, board):
    box = Box(color=color, posX=pos_x, posY=pos_y, idGame=game.id, idBoard=board.id)
    session.add(box)
    session.flush()
    return box

def create_movement_card(description, used, player):
    session = Session()
    try:
        card = MovementCard(description=description, used=used, idPlayer=player.id)
        session.add(card)
        session.flush()
    finally:
        session.close()
    return card

def create_figure_card(show, difficulty, player, game):
    session = Session()
    try:
        card = FigureCard(show=show, difficulty=difficulty, player_id=player.id, game_id=game.id)
        session.add(card)
        session.flush()
    finally:
        session.close()
    return card

# Populate the database with sample data
def populate_database():
    session = SessionLocal()
    try:
        # Create a game
        game = create_game("Test Game", 2, 4)

        # Create game state
        game_state = create_game_state(game, StateEnum.PLAYING)

        # Create players
        players = [
            create_player(f"Player {i}", game, game_state, turn, i == 0)
            for i, turn in enumerate([turnEnum.PRIMERO, turnEnum.SEGUNDO, turnEnum.TERCERO, turnEnum.CUARTO])
        ]

        # Set current player
        game_state.current_player = players[0].id

        # Create board
        board = create_board(game)

        # Create boxes
        colors = list(ColorEnum)
        for x in range(6):
            for y in range(6):
                create_box(random.choice(colors), x, y, game, board)

        # Create movement cards
        movements = ["DER_ESP", "IZQ_ESP", "EN_L_ESP", "DIAG"]
        for player in players:
            for _ in range(3):
                create_movement_card(random.choice(movements), False, player)

        # Create figure cards
        for player in players:
            for _ in range(2):
                create_figure_card(False, random.choice(list(DifficultyEnum)), player, game)

        # Commit the session
        session.commit()
    except Exception as e:
        print(f"An error ocurred: {e}")
        session.rollback()
        
if __name__ == "__main__":
    populate_database()
    print("Database populated with test data.")
from enum import Enum

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import db

from board.models import Box, ColorEnum
from figureCards.models import FigureCard, DifficultyEnum
from game.models import Game
from gameState.models import GameState, StateEnum
from movementCards.models import MovementCard
from player.models import Player

from database.converter import EnumConverter

from game.endpoints import game_router

app = FastAPI()

#Allow cross-origin requests (Needed to connect to React app)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(game_router)

@app.get("/")
async def root():
    return {"message": "El Switcher"}

# Bindear la database
db.bind(provider="sqlite", filename="db.sqlite", create_db=True) # ver filename

db.provider.converter_classes.append((Enum, EnumConverter))

# Generar los mappings y crear las tables
db.generate_mapping(create_tables=True)
import random
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.db import get_db
from .models import Board, Box
from .schemas import BoxOut
from .board_repository import BoardRepository

board_router = APIRouter(
    prefix="/board",
    tags=['Board']
)


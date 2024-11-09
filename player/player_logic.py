from .models import turnEnum
import random
from .player_repository import PlayerRepository 
from sqlalchemy.orm import Session
from database.db import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import os
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_player_logic(player_repo: PlayerRepository = Depends()):
    return PlayerLogic(player_repo)

class PlayerLogic:
    def __init__(self, player_repo: PlayerRepository):
        self.player_repo = player_repo

    def assign_random_turns(self, players, db: Session):
        randomTurns = random.sample(range(1, len(players) + 1), len(players))
        turnMapping = {1: turnEnum.PRIMERO, 2: turnEnum.SEGUNDO, 3: turnEnum.TERCERO, 4: turnEnum.CUARTO}
        
        firstPlayer = None
        
        for player, turn in zip(players, randomTurns):
            self.player_repo.assign_turn_player(player.game_id, player.id, turnMapping[turn], db)
            if turn == 1:
                firstPlayer = player
        
        return firstPlayer.id
    
    @staticmethod
    def create_access_token(player_id: int, expires_delta: Optional[timedelta] = None):
        to_encode = {"sub": str(player_id)}
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload  
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

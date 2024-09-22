from pydantic import BaseModel

class MovementCardSchema(BaseModel):
    id: int
    description: str
    used: bool
    player_id: int
    game_id: int
    
    class Config:
        from_attributes = True
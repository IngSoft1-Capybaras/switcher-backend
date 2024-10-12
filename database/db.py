from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from settings import DATABASE_FILENAME

# Crear una engine sqlalchemy

engine = create_engine(f'sqlite:///./{DATABASE_FILENAME}', echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    import board.models
    import game.models
    import gameState.models
    import player.models
    import figureCards.models
    import movementCards.models
    Base.metadata.create_all(engine)
    
def get_db(session=None):
    if session:
        try:
            yield session
        finally:
            pass
    else:
        db= SessionLocal()
        try:
            yield db
        finally:
            db.close()
        
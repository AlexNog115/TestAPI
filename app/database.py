from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Creates the BD engine in SQLAlchemy 
engine = create_engine(settings.DATABASE_URL)

# creates a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the base class for declarative models
Base = declarative_base()

# Function to get a database session
def get_db():
    """
    It creates a database session and makes sure to close it
    when it is finished using it.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
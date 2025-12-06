from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variables. 
# If not found, default to a local postgres connection string.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5433/stock_db")

# Create the SQLAlchemy engine. This is the core interface to the database.
# It manages the connection pool and dialect (PostgreSQL in this case).
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# Create a SessionLocal class. Each instance of this class will be a database session.
# autocommit=False: We want to manually commit changes to ensure transaction integrity.
# autoflush=False: We want to manually flush changes to the DB.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models. All models will inherit from this.
Base = declarative_base()

# Dependency function to get a database session.
# This is used in FastAPI path operations to ensure each request gets its own session
# and that the session is closed after the request is finished.
def get_db():
    db = SessionLocal()
    try:
        yield db # Yield the session to the path operation
    finally:
        db.close() # Ensure the session is closed even if an error occurs

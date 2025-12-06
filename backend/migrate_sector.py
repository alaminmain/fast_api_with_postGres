from sqlalchemy import create_engine, text
from app.models import Base
from dotenv import load_dotenv
import os
import sys

# Load environment variables (to get DATABASE_URL)
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    print("Error: DATABASE_URL not found in .env")
    sys.exit(1)

# Initialize Engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

def migrate():
    # 1. Create new tables (sectors, fundamentals) if they don't exist
    # Base.metadata.create_all checks existence and creates only new tables
    print("Creating new tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables 'sectors' and 'fundamentals' created (if missing).")
    except Exception as e:
        print(f"Error creating tables: {e}")

    # 2. Add 'sector_id' column to 'stocks' table if it doesn't exist
    print("Checking 'stocks' table for 'sector_id' column...")
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='stocks' AND column_name='sector_id'"))
            if result.fetchone():
                print("'sector_id' column already exists in 'stocks' table.")
            else:
                print("Adding 'sector_id' column to 'stocks' table...")
                conn.execute(text("ALTER TABLE stocks ADD COLUMN sector_id INTEGER REFERENCES sectors(id)"))
                conn.commit()
                print("'sector_id' column added successfully.")
        except Exception as e:
            print(f"Error altering table: {e}")

if __name__ == "__main__":
    migrate()

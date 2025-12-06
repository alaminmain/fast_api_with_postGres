import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Get the database URL
database_url = os.getenv("DATABASE_URL")

print(f"Testing connection with: {database_url}")

if not database_url:
    print("Error: DATABASE_URL not found in environment variables.")
    exit(1)

try:
    engine = create_engine(database_url)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("\n✅ Connection successful! Database is accessible.")
except Exception as e:
    print("\n❌ Connection failed.")
    print(f"Error: {e}")

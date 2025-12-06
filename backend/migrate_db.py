from app.database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        print("Migrating schema...")
        try:
            conn.execute(text("ALTER TABLE transactions ADD COLUMN user_id INTEGER REFERENCES users(id)"))
            print("Added user_id to transactions")
        except Exception as e:
            print(f"Error altering transactions (might already exist): {e}")

        try:
            conn.execute(text("ALTER TABLE watchlist ADD COLUMN user_id INTEGER REFERENCES users(id)"))
            print("Added user_id to watchlist")
        except Exception as e:
            print(f"Error altering watchlist (might already exist): {e}")

        try:
            conn.execute(text("ALTER TABLE alerts ADD COLUMN user_id INTEGER REFERENCES users(id)"))
            print("Added user_id to alerts")
        except Exception as e:
            print(f"Error altering alerts (might already exist): {e}")
            
        conn.commit()
        print("Migration complete.")

if __name__ == "__main__":
    migrate()

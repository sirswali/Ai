import os
import sqlite3
from dotenv import load_dotenv

print("Starting database test script...")

# Load environment variables
load_dotenv()
print("Environment variables loaded")

# Set up database path
current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv('DATABASE_URL', os.path.join(current_dir, 'test_database.db'))
# Remove the 'sqlite:///' prefix if it exists
if DB_PATH.startswith('sqlite:///'):
    DB_PATH = DB_PATH[10:]
print(f"Database path: {DB_PATH}")

def get_db_connection():
    try:
        print(f"Attempting to connect to database at {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        print("Database connection established")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    print("Initializing database...")
    conn = get_db_connection()
    if conn is None:
        print("Failed to initialize database")
        return False

    try:
        # Check if the database is already initialized
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone() is not None:
            print("Database already initialized")
            return True

        # If not initialized, create the tables
        print("Creating tables...")
        create_tables_path = os.path.join(current_dir, 'create_tables.sql')
        print(f"Loading SQL from {create_tables_path}")
        with open(create_tables_path, 'r') as f:
            conn.executescript(f.read())
        
        conn.commit()
        print("Database initialized successfully")
        return True
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    if init_db():
        print("Database initialization successful")
    else:
        print("Database initialization failed")

print("Script execution completed")

import sqlite3

# DB_FILE = "/home/project4/Desktop/d1.db"
DB_FILE = "app.db"
def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Allows access by column name
    return conn

def modify_database():
    """Initialize the database and create tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    with open('schema.sql', 'r') as f:
        schema = f.read()
    cursor.executescript(schema)
    conn.commit()
    conn.close()

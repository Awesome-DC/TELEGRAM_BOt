import sqlite3
from sqlite3 import Connection
from datetime import datetime
import random
import string
DB_NAME = "bot.db"

# -----------------------------
# Connection helper
# -----------------------------
def get_connection() -> Connection:
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # access columns by name
    return conn

# -----------------------------
# Create tables
# -----------------------------
def create_tables():
    """Create users table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        rank TEXT DEFAULT 'Member',
        coins INTEGER DEFAULT 10,
        current_game TEXT,
        last_play TIMESTAMP,
        last_chat_id INTEGER
    );
    """)
    conn.commit()
    conn.close()

# -----------------------------
# Add a new user
# -----------------------------
def add_user(user_id: int, username: str = None, starter_coins: int = 10):
    """Add a new user if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO users (user_id, username, coins, last_play)
    VALUES (?, ?, ?, ?)
    """, (user_id, username, starter_coins, datetime.now()))
    conn.commit()
    conn.close()

# -----------------------------
# Fetch user info
# -----------------------------
def get_user(user_id: int):
    """Fetch user info as a dictionary."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# -----------------------------
# Update user coins
# -----------------------------
def update_coins(user_id: int, coins: int):
    """Update a user's coin balance."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET coins = ? WHERE user_id = ?", (coins, user_id))
    conn.commit()
    conn.close()

# -----------------------------
# Update current game state
# -----------------------------
def update_game_state(user_id: int, game_state: str):
    """Update the current game state for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET current_game = ?, last_play = ? WHERE user_id = ?",
                   (game_state, datetime.now(), user_id))
    conn.commit()
    conn.close()

def reset_all_coins():
    """Set coins of all users to 0."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET coins = 0")
    conn.commit()
    conn.close()


# -----------------------------
# Update last chat id
# -----------------------------
def update_last_chat(user_id: int, chat_id: int):
    """Save the last chat ID the user interacted in."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET last_chat_id = ? WHERE user_id = ?", (chat_id, user_id))
    conn.commit()
    conn.close()

def create_redeem_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS redeem_codes (
        code TEXT PRIMARY KEY,
        coins INTEGER NOT NULL,
        used_by INTEGER DEFAULT NULL
    );
    """)
    conn.commit()
    conn.close()


# -----------------------------
# Get all users
# -----------------------------
def get_all_users():
    """Return a list of all users."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def set_rank(user_id: int, rank: str):
    """Set the rank/status of a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET rank = ? WHERE user_id = ?", (rank, user_id))
    conn.commit()
    conn.close()

def generate_code(length=10):
    """Generate a random alphanumeric code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def add_redeem_code(code: str, coins: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO redeem_codes (code, coins) VALUES (?, ?)", (code, coins))
    conn.commit()
    conn.close()

def get_redeem_code(code: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM redeem_codes WHERE code = ?", (code,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def mark_code_used(code: str, user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE redeem_codes SET used_by = ? WHERE code = ?", (user_id, code))
    conn.commit()
    conn.close()

def create_redeem_table():
    """Create redeem_codes table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS redeem_codes (
        code TEXT PRIMARY KEY,
        coins INTEGER NOT NULL,
        used_by INTEGER DEFAULT NULL
    );
    """)
    conn.commit()
    conn.close()

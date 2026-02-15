from db import get_connection

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

import os
import sqlite3

default_db = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "state", "wargame.db"))
DB_PATH = os.environ.get("DB_PATH", default_db)

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_state (
            id INTEGER PRIMARY KEY,
            run_id INTEGER DEFAULT 1,
            defcon_level INTEGER DEFAULT 5,
            simulation_active BOOLEAN DEFAULT 0,
            countdown_start_time INTEGER DEFAULT 0,
            countdown_deadline INTEGER DEFAULT 0,
            auth_deadline INTEGER DEFAULT 0,
            simulation_result TEXT DEFAULT '',
            final_puzzle_active BOOLEAN DEFAULT 0,
            final_puzzle_solved BOOLEAN DEFAULT 0,
            puzzle_board TEXT DEFAULT '         ',
            authorization_accepted BOOLEAN DEFAULT 0,
            completion_status BOOLEAN DEFAULT 0,
            timeout_status BOOLEAN DEFAULT 0,
            is_aborted BOOLEAN DEFAULT 0,
            is_timeout BOOLEAN DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            ended_at INTEGER,
            status TEXT
        )
    """)
    # Ensure all columns exist if table was created in an earlier migration
    cursor.execute("PRAGMA table_info(game_state)")
    columns = [row[1] for row in cursor.fetchall()]
    new_cols = [
        ("run_id", "INTEGER DEFAULT 1"),
        ("auth_deadline", "INTEGER DEFAULT 0"),
        ("simulation_result", "TEXT DEFAULT ''"),
        ("final_puzzle_active", "BOOLEAN DEFAULT 0"),
        ("final_puzzle_solved", "BOOLEAN DEFAULT 0"),
        ("puzzle_board", "TEXT DEFAULT '         '"),
        ("authorization_accepted", "BOOLEAN DEFAULT 0"),
        ("completion_status", "BOOLEAN DEFAULT 0"),
        ("timeout_status", "BOOLEAN DEFAULT 0"),
    ]
    for col_name, col_type in new_cols:
        if col_name not in columns:
            cursor.execute(f"ALTER TABLE game_state ADD COLUMN {col_name} {col_type}")

    # Insert default row if not exists
    cursor.execute("SELECT id FROM game_state WHERE id = 1")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO game_state (id) VALUES (1)")
    conn.commit()
    conn.close()

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn

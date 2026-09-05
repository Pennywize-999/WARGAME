import os
import sys
import sqlite3

def init_clean_production_db(db_path="state/wargame.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE game_state (
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
    
    cur.execute("""
        CREATE TABLE runs_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            ended_at INTEGER,
            status TEXT
        )
    """)
    
    cur.execute("""
        INSERT INTO game_state (
            id, run_id, defcon_level, simulation_active,
            countdown_start_time, countdown_deadline, auth_deadline,
            simulation_result, final_puzzle_active, final_puzzle_solved,
            puzzle_board, authorization_accepted, completion_status,
            timeout_status, is_aborted, is_timeout
        ) VALUES (1, 1, 5, 0, 0, 0, 0, '', 0, 0, '         ', 0, 0, 0, 0, 0)
    """)
    
    conn.commit()
    
    cur.execute("SELECT run_id, defcon_level, simulation_active FROM game_state WHERE id=1")
    row = cur.fetchone()
    cur.execute("SELECT count(*) FROM runs_history")
    count = cur.fetchone()[0]
    conn.close()
    
    assert row == (1, 5, 0), f"Unexpected game_state: {row}"
    assert count == 0, f"runs_history is not empty: {count}"
    print(f"[+] Pristine production database initialized at: {db_path}")
    print(f"    run_id: {row[0]}, defcon_level: {row[1]}, history_rows: {count}")

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else "state/wargame.db"
    init_clean_production_db(target)
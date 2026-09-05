import os
import time
import sqlite3
from .db import get_connection

GAME_DURATION = 420  # 7 minutes = 420 seconds

def get_flag():
    flag = os.environ.get("FLAG")
    if not flag:
        raise RuntimeError(
            "FLAG environment variable is not configured. "
            "Deployment must set FLAG before running WOPR."
        )
    return flag

def get_defcon():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT defcon_level FROM game_state WHERE id = 1")
    res = cur.fetchone()
    conn.close()
    return res[0] if res else 5

def set_defcon(level):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE game_state SET defcon_level = ? WHERE id = 1", (level,))
    conn.commit()
    conn.close()

def advance_defcon(current_level, new_level):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE game_state SET defcon_level = ? WHERE id = 1 AND defcon_level = ?", (new_level, current_level))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def reset_state():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE game_state SET 
            defcon_level = 5,
            simulation_active = 0,
            countdown_start_time = 0,
            countdown_deadline = 0,
            auth_deadline = 0,
            simulation_result = '',
            final_puzzle_active = 0,
            final_puzzle_solved = 0,
            puzzle_board = '         ',
            authorization_accepted = 0,
            completion_status = 0,
            timeout_status = 0,
            is_aborted = 0,
            is_timeout = 0
        WHERE id = 1
    """)
    conn.commit()
    conn.close()

def get_state():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM game_state WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def start_simulation():
    conn = get_connection()
    cur = conn.cursor()
    now = int(time.time())
    deadline = now + GAME_DURATION
    cur.execute("""
        UPDATE game_state 
        SET simulation_active = 1,
            countdown_start_time = ?,
            countdown_deadline = ?,
            auth_deadline = 0,
            simulation_result = '',
            final_puzzle_active = 0,
            final_puzzle_solved = 0,
            puzzle_board = '         ',
            authorization_accepted = 0,
            completion_status = 0,
            timeout_status = 0,
            is_aborted = 0,
            is_timeout = 0
        WHERE id = 1 AND defcon_level = 1 AND simulation_active = 0
    """, (now, deadline))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def activate_final_puzzle():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE game_state 
        SET simulation_result = 'WINNER: NONE',
            final_puzzle_active = 1
        WHERE id = 1 AND simulation_active = 1 AND final_puzzle_active = 0
    """)
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def update_puzzle_board(board_str: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE game_state
        SET puzzle_board = ?
        WHERE id = 1 AND simulation_active = 1 AND final_puzzle_active = 1
    """, (board_str,))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def solve_final_puzzle(auth_deadline: int = 0):
    conn = get_connection()
    cur = conn.cursor()
    if auth_deadline == 0:
        auth_deadline = int(time.time()) + 20
    cur.execute("""
        UPDATE game_state 
        SET final_puzzle_solved = 1,
            simulation_result = 'WINNER: X',
            auth_deadline = ?
        WHERE id = 1 AND simulation_active = 1 AND final_puzzle_active = 1 AND final_puzzle_solved = 0
    """, (auth_deadline,))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def abort_simulation():
    conn = get_connection()
    cur = conn.cursor()
    now = int(time.time())
    cur.execute("""
        UPDATE game_state 
        SET simulation_active = 0,
            final_puzzle_active = 0,
            authorization_accepted = 1,
            completion_status = 1,
            is_aborted = 1,
            defcon_level = 5
        WHERE id = 1
          AND simulation_active = 1
          AND final_puzzle_solved = 1
          AND authorization_accepted = 0
          AND completion_status = 0
          AND timeout_status = 0
          AND auth_deadline >= ?
    """, (now,))
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def trigger_timeout():
    conn = get_connection()
    cur = conn.cursor()
    now = int(time.time())
    cur.execute("SELECT run_id FROM game_state WHERE id = 1 AND simulation_active = 1")
    row = cur.fetchone()
    if not row:
        conn.close()
        return False
    current_run_id = row[0] if row[0] is not None else 1
    cur.execute(
        "INSERT INTO runs_history (run_id, ended_at, status) VALUES (?, ?, 'EXPIRED_TIMEOUT')",
        (current_run_id, now)
    )
    cur.execute("""
        UPDATE game_state SET 
            run_id = run_id + 1,
            defcon_level = 5,
            simulation_active = 0,
            countdown_start_time = 0,
            countdown_deadline = 0,
            auth_deadline = 0,
            simulation_result = '',
            final_puzzle_active = 0,
            final_puzzle_solved = 0,
            puzzle_board = '         ',
            authorization_accepted = 0,
            completion_status = 0,
            timeout_status = 0,
            is_aborted = 0,
            is_timeout = 1
        WHERE id = 1 AND simulation_active = 1
    """)
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def trigger_auth_timeout():
    conn = get_connection()
    cur = conn.cursor()
    now = int(time.time())
    cur.execute("SELECT run_id FROM game_state WHERE id = 1 AND simulation_active = 1 AND final_puzzle_solved = 1")
    row = cur.fetchone()
    if not row:
        conn.close()
        return False
    current_run_id = row[0] if row[0] is not None else 1
    cur.execute(
        "INSERT INTO runs_history (run_id, ended_at, status) VALUES (?, ?, 'AUTH_TIMEOUT')",
        (current_run_id, now)
    )
    cur.execute("""
        UPDATE game_state SET 
            run_id = run_id + 1,
            defcon_level = 5,
            simulation_active = 0,
            countdown_start_time = 0,
            countdown_deadline = 0,
            auth_deadline = 0,
            simulation_result = '',
            final_puzzle_active = 0,
            final_puzzle_solved = 0,
            puzzle_board = '         ',
            authorization_accepted = 0,
            completion_status = 0,
            timeout_status = 0,
            is_aborted = 0,
            is_timeout = 1
        WHERE id = 1 AND simulation_active = 1
    """)
    affected = cur.rowcount
    conn.commit()
    conn.close()
    return affected > 0
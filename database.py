import sqlite3
import os

DB_PATH = 'career_system.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=None, fetch=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = [dict(row) for row in cursor.fetchall()]
        else:
            conn.commit()
            result = cursor.lastrowid
        return result
    except Exception as e:
        print(f"Database Error: {e}")
        return [] if fetch else None
    finally:
        conn.close()

import sqlite3

from default import PATH

DB_PATH = PATH["chat_history"] / "chat_history.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

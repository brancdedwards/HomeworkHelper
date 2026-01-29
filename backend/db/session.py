import sqlite3
from contextlib import contextmanager
from backend.app.core.settings import settings

@contextmanager
def get_db():
    conn = sqlite3.connect(str(settings.DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()
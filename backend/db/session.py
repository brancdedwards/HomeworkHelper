import sqlite3
from contextlib import contextmanager
# from backend.app.core import settings
from backend.app.core.settings import settings

DB_PATH = settings.DB_PATH

@contextmanager
def get_db():
    conn = sqlite3.connect(str(DB_PATH))  # Use the path from settings
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

# /Users/brandonedwards/Library/CloudStorage/OneDrive-Personal/Python Projects/GitHub/PythonProject/HomeworkHelper/backend/db/session.py
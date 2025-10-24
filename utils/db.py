import os, sqlite3
from datetime import datetime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean


DB_PATH = 'data/homework_helper.db'
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_prompt_template(category: str, topic: str = None):
    """
    Retrieve a prompt_template from the prompts table.
    Falls back to category-only match if topic not found.
    """
    from utils.db import get_connection
    conn = get_connection()
    cur = conn.cursor()
    if topic:
        cur.execute("""
            SELECT prompt_template 
            FROM prompts 
            WHERE LOWER(category) = LOWER(?) 
              AND LOWER(topic) = LOWER(?)
            LIMIT 1;
        """, (category, topic))
        row = cur.fetchone()
        if row:
            return row[0]

    # fallback: just category
    cur.execute("""
        SELECT prompt_template 
        FROM prompts 
        WHERE LOWER(category) = LOWER(?) 
        ORDER BY id DESC LIMIT 1;
    """, (category,))
    row = cur.fetchone()
    return row[0] if row else None

def get_prompt_for_topic(conn, category, topic):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT prompt_template, example
        FROM prompts
        WHERE LOWER(category) = LOWER(?) AND LOWER(topic) = LOWER(?)
        LIMIT 1;
    """, (category, topic))
    row = cursor.fetchone()
    if not row:
        return None, None
    return row[0], row[1]

# ORM model definitions
class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    topic = Column(String)
    passages = relationship("Passage", back_populates="session")

class Passage(Base):
    __tablename__ = "passages"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    original_text = Column(Text)
    simplified_text = Column(Text)
    session = relationship("Session", back_populates="passages")
    questions = relationship("Question", back_populates="passage")
    words = relationship("Word", back_populates="passage")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    passage_id = Column(Integer, ForeignKey("passages.id"))
    question_text = Column(Text)
    passage = relationship("Passage", back_populates="questions")

class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True)
    passage_id = Column(Integer, ForeignKey("passages.id"))
    word = Column(String)
    explanation = Column(Text)
    passage = relationship("Passage", back_populates="words")

class Concept(Base):
    __tablename__ = "concepts"
    id = Column(Integer, primary_key=True)
    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime)
    subject = Column(String, nullable=False)
    topic = Column(Text, nullable=False)
    type = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    subject = Column(String, nullable=True)
    grade_level = Column(Integer, nullable=True)
    active = Column(Boolean, default=True)
    last_seen_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "homework_helper.db")

def log_attempt(
    subject,
    topic,
    question_text,
    user_answer,
    correct_answer,
    is_correct,
    hint_used=False,
    question_type="multiple_choice"
):
    """Logs a learning attempt across any subject."""
    # Ensure the attempts table exists
    conn = conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS attempts
                (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject          TEXT NOT NULL,
                    topic            TEXT,
                    question_type    TEXT,
                    question_text    TEXT NOT NULL,
                    user_answer      TEXT,
                    correct_answer   TEXT,
                    is_correct       BOOLEAN,
                    hint_used        BOOLEAN   DEFAULT 0,
                    difficulty_level TEXT      DEFAULT 'normal',
                    attempt_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)

    # Insert the attempt
    cur.execute("""
        INSERT INTO attempts
        (subject, topic, question_type, question_text, user_answer, correct_answer, is_correct, hint_used, attempt_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        subject,
        topic,
        question_type,
        question_text,
        user_answer,
        correct_answer,
        int(is_correct),
        int(hint_used),
        datetime.now()
    ))

    # Commit and close cleanly
    conn.commit()
    conn.close()

def fetch_attempts_summary():
    conn = conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT subject, topic,
               COUNT(*) AS total,
               SUM(is_correct) AS correct,
               ROUND(SUM(is_correct)*100.0/COUNT(*), 1) AS accuracy_pct
        FROM attempts
        GROUP BY subject, topic
        ORDER BY subject, accuracy_pct ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_recent_attempts(days=7):
    conn = conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT subject, topic, question_text, user_answer, correct_answer, is_correct, attempt_date
        FROM attempts
        WHERE attempt_date >= datetime('now', ?)
        ORDER BY attempt_date DESC
    """, (f'-{days} days',))
    rows = cur.fetchall()
    conn.close()
    return rows
# Create tables
Base.metadata.create_all(engine)

"""
attempts_repository.py

Provides DB access for logging practice attempts.
This is the lowest-level data layer and contains no business logic.
"""

from backend.db.session import get_db


def _normalize_topic(topic: str | None):
    if not topic:
        return topic
    return topic.replace("_", " ").strip().title()


def create_attempt(payload):
    """
    Insert a new practice attempt into the attempts table.
    Accepts a Pydantic model or dict‑like object.
    Uses model_dump() when available.
    Returns the new attempt ID.
    """
    # Normalize payload into a dict
    if hasattr(payload, "model_dump"):
        data = payload.model_dump()
    else:
        data = dict(payload)

    # Normalize topic before insert
    data["topic"] = _normalize_topic(data.get("topic"))

    with get_db() as db:
        cur = db.execute("""
            INSERT INTO attempts (
                subject,
                topic,
                question_type,
                question_text,
                user_answer,
                correct_answer,
                is_correct,
                hint_used,
                difficulty_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("subject"),
            data.get("topic"),
            data.get("question_type"),
            data.get("question_text"),
            data.get("user_answer"),
            data.get("correct_answer"),
            int(data.get("is_correct", 0)),
            int(data.get("hint_used", 0)),
            data.get("difficulty_level", "normal")
        ))

        return cur.lastrowid
def list_attempts():
    with get_db() as db:
        cur = db.execute("SELECT * FROM attempts ORDER BY attempt_date DESC")
        rows = cur.fetchall()
        return [dict(r) for r in rows]

def get_stats():
    with get_db() as db:

        # Overall totals
        total = db.execute("SELECT COUNT(*) FROM attempts").fetchone()[0]
        correct = db.execute("SELECT COUNT(*) FROM attempts WHERE is_correct=1").fetchone()[0]
        accuracy = (correct / total) * 100 if total > 0 else 0

        # Stats by topic
        topic_stats = db.execute("""
            SELECT 
                topic,
                COUNT(*) AS total,
                SUM(is_correct) AS correct,
                ROUND((SUM(is_correct) * 100.0) / COUNT(*), 1) AS accuracy_pct
            FROM attempts
            GROUP BY topic
            ORDER BY accuracy_pct DESC
        """).fetchall()

        # Stats by subject
        subject_stats = db.execute("""
            SELECT 
                subject,
                COUNT(*) AS total,
                SUM(is_correct) AS correct,
                ROUND((SUM(is_correct) * 100.0) / COUNT(*), 1) AS accuracy_pct
            FROM attempts
            GROUP BY subject
            ORDER BY accuracy_pct DESC
        """).fetchall()

        return {
            "overall": {
                "total_attempts": total,
                "correct": correct,
                "accuracy_pct": round(accuracy, 1)
            },
            "by_topic": [dict(r) for r in topic_stats],
            "by_subject": [dict(r) for r in subject_stats]
        }

def list_attempts_filtered(subject=None, topic=None, difficulty=None, correct=None):
    query = "SELECT * FROM attempts WHERE 1=1"
    params = []

    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if topic:
        query += " AND topic = ?"
        params.append(_normalize_topic(topic))
    if difficulty:
        query += " AND difficulty_level = ?"
        params.append(difficulty)
    if correct is not None:
        query += " AND is_correct = ?"
        params.append(1 if correct else 0)

    query += " ORDER BY attempt_date DESC"

    with get_db() as db:
        cur = db.execute(query, params)
        return [dict(r) for r in cur.fetchall()]

def get_attempt_by_id(attempt_id: int):
    with get_db() as db:
        cur = db.execute(
            "SELECT * FROM attempts WHERE id = ?",
            (attempt_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None
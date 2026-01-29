from backend.db.session import get_db
from backend.app.schemas.topic import TopicIn, TopicOut

def get_all_topics():
    with get_db() as db:
        rows = db.execute("SELECT id, name, category, question_focus, active FROM topics").fetchall()
        return [TopicOut(**dict(r)) for r in rows]

def create_topic(payload: TopicIn):
    with get_db() as db:
        cur = db.execute("""
            INSERT INTO topics (name, category, question_focus, active)
            VALUES (?, ?, ?, ?)
        """, (payload.name, payload.category, payload.question_focus, payload.active))
        new_id = cur.lastrowid
        return TopicOut(id=new_id, **payload.dict())

def update_topic(topic_id, payload: TopicIn):
    with get_db() as db:
        db.execute("""
            UPDATE topics 
            SET name=?, category=?, question_focus=?, active=?
            WHERE id=?
        """, (payload.name, payload.category, payload.question_focus, payload.active, topic_id))
        return TopicOut(id=topic_id, **payload.dict())

def deactivate_topic(topic_id):
    with get_db() as db:
        db.execute("UPDATE topics SET active=0 WHERE id=?", (topic_id,))


# New function to fetch complete topic metadata for question generation
def get_topic_data(topic_name: str, subject: str = "grammar"):
    """
    Fetch a complete topic record for grammar question generation.
    Returns topic metadata including name, category, question_focus,
    prompt_template, and example.
    """
    with get_db() as db:
        row = db.execute("""
            SELECT
                id, name, subject, category, question_focus,
                prompt_template, example, active
            FROM topics
            WHERE LOWER(name) = LOWER(?)
              AND subject = ?
              AND active = 1
        """, (topic_name, subject)).fetchone()

        if not row:
            return None

        return dict(row)
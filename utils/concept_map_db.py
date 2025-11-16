import os
import sqlite3

# Path to your SQLite database
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/homework_helper.db")

def get_concept(topic: str, subject: str = "grammar"):
    """
    Retrieve a concept by exact or fuzzy topic match from the DB.

    Strategy:
    1) Try exact matches against `topics.name` using normalized variants.
    2) If not found, try wildcard LIKE matches.
    3) If still not found, fallback to partial match joining `topics` and `concepts`
       for grade level and notes.

    Returns a dict like:
      {"subject": ..., "category": ..., "topic": ..., "question_focus": ..., "grade_level": ..., "notes": ...}
    or None if nothing is found.
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")

    # --- helpers -----------------------------------------------------------
    def _normalize(s: str) -> str:
        return (s or "").strip().lower().replace("-", "_")

    def _variants(s: str):
        s = _normalize(s)
        cand = {s}
        if s.endswith("s"):
            cand.add(s[:-1])
        else:
            cand.add(s + "s")
        cand.add(s.replace("_sentence", "_sentences"))
        cand.add(s.replace("_sentences", "_sentence"))
        alias = {
            "adverb": "adjectives_and_adverbs",
            "adverbs": "adjectives_and_adverbs",
            "run_on_sentence": "run_on_sentences",
            "quotation_mark": "quotation_marks",
            "semicolon": "semicolons",
            "colon": "colons",
        }
        if s in alias:
            cand.add(_normalize(alias[s]))
        return [c for c in sorted(cand) if c]

    # ----------------------------------------------------------------------
    topic_variants = _variants(topic)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1) Exact match in topics
    try:
        placeholders = ",".join(["?"] * len(topic_variants))
        sql_exact = f"""
            SELECT t.subject, t.category, t.name, t.question_focus, t.grade_level, ''
            FROM topics t
            WHERE t.subject = ?
              AND LOWER(t.name) IN ({placeholders})
            LIMIT 1;
        """
        cursor.execute(sql_exact, [subject] + topic_variants)
        row = cursor.fetchone()
        if row:
            conn.close()
            return {
                "subject": row[0],
                "category": row[1],
                "topic": row[2],
                "question_focus": row[3],
                "grade_level": row[4],
                "notes": row[5],
            }
    except Exception:
        pass

    # 2) Fuzzy (LIKE) match in topics
    try:
        like_variants = [f"%{v}%" for v in topic_variants]
        placeholders = " OR ".join([f"LOWER(t.name) LIKE ?" for _ in like_variants])
        sql_like = f"""
            SELECT t.subject, t.category, t.name, t.question_focus, t.grade_level, ''
            FROM topics t
            WHERE t.subject = ?
              AND ({placeholders})
            LIMIT 1;
        """
        cursor.execute(sql_like, [subject] + like_variants)
        row = cursor.fetchone()
        if row:
            conn.close()
            return {
                "subject": row[0],
                "category": row[1],
                "topic": row[2],
                "question_focus": row[3],
                "grade_level": row[4],
                "notes": row[5],
            }
    except Exception:
        pass

    # 3) Fallback: partial match with metadata from topics & concepts
    try:
        like_variants = [f"%{v}%" for v in topic_variants]
        where_clause = " OR ".join(["LOWER(t.name) LIKE ?"] * len(like_variants))
        sql_join = f"""
            SELECT 
                t.subject,
                t.category,
                t.name AS topic,
                t.question_focus,
                t.grade_level,
                COALESCE(c.notes, '') AS notes
            FROM topics t
            LEFT JOIN concepts c 
                ON c.subject = t.subject
               AND LOWER(c.topic) = LOWER(t.name)
            WHERE t.subject = ?
              AND ({where_clause})
            ORDER BY t.grade_level IS NULL, t.name
            LIMIT 1;
        """
        cursor.execute(sql_join, [subject] + like_variants)
        row = cursor.fetchone()
        if row:
            conn.close()
            return {
                "subject": row[0],
                "category": row[1],
                "topic": row[2],
                "question_focus": row[3],
                "grade_level": row[4],
                "notes": row[5],
            }
    except Exception:
        pass

    conn.close()
    return None
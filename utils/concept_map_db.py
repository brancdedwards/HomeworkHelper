import os
import sqlite3

# Path to your SQLite database
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/homework_helper.db")

def get_concept(topic: str, subject: str = "grammar"):
    """
    Retrieve a concept by exact or fuzzy topic match from the DB.

    Strategy:
    1) Try exact matches against `concept_map.topic` using a set of
       normalized variants (handles singular/plural & common aliases).
    2) If not found, try wildcard LIKE matches.
    3) If still not found, try a join against `topics.name` and
       `concepts.topic` to recover a matching concept and its metadata.

    Returns a dict like:
      {"category": ..., "question_focus": ...}
    or a richer dict:
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

        # singular/plural toggles
        if s.endswith("s"):
            cand.add(s[:-1])               # antonyms -> antonym, pronouns -> pronoun
        else:
            cand.add(s + "s")              # antonym -> antonyms

        # sentence / sentences toggles
        cand.add(s.replace("_sentence", "_sentences"))
        cand.add(s.replace("_sentences", "_sentence"))

        # common aliases map
        alias = {
            "adverb": "adjectives_and_adverbs",
            "adverbs": "adjectives_and_adverbs",
            "run_on_sentence": "run_on_sentences",
            "quotation_mark": "quotation_marks",
            "semicolon": "semicolons",   # in case you ever store plural
            "colon": "colons",
        }
        if s in alias:
            cand.add(_normalize(alias[s]))

        # drop empties and dedupe
        return [c for c in sorted(cand) if c]

    # ----------------------------------------------------------------------
    topic_variants = _variants(topic)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1) Exact match against concept_map.topic
    try:
        placeholders = ",".join(["?"] * len(topic_variants))
        sql_exact = f"""
            SELECT cm.subject, cm.category, cm.topic, cm.question_focus
            FROM concept_map cm
            WHERE cm.subject = ?
              AND LOWER(cm.topic) IN ({placeholders})
            LIMIT 1
        """
        cursor.execute(sql_exact, [subject] + [v for v in topic_variants])
        row = cursor.fetchone()
        if row:
            conn.close()
            return {
                "subject": row[0],
                "category": row[1],
                "topic": row[2],
                "question_focus": row[3],
            }
    except Exception:
        pass  # fall through to fuzzy/join attempts

    # 2) LIKE (fuzzy) match against concept_map.topic
    try:
        like_variants = [f"%{v}%" for v in topic_variants]
        placeholders = " OR ".join([f"LOWER(cm.topic) LIKE ?" for _ in like_variants])
        sql_like = f"""
            SELECT cm.subject, cm.category, cm.topic, cm.question_focus
            FROM concept_map cm
            WHERE cm.subject = ?
              AND ({placeholders})
            LIMIT 1
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
            }
    except Exception:
        pass  # fall through to join attempt

    # 3) Join with topics (t.name) and concepts (c.topic)
    try:
        # Note: topics has column `name` (not `topic`); concepts has `topic`.
        # topics contains `grade_level`; concepts may contain `notes`.
        like_variants = [f"%{v}%" for v in topic_variants]
        placeholders_cm = " OR ".join([f"LOWER(cm.topic) LIKE ?" for _ in like_variants])
        placeholders_t = " OR ".join([f"LOWER(t.name) LIKE ?" for _ in like_variants])
        placeholders_c = " OR ".join([f"LOWER(c.topic) LIKE ?" for _ in like_variants])

        sql_join = f"""
            SELECT cm.subject, cm.category, cm.topic, cm.question_focus,
                   t.grade_level, c.notes
            FROM concept_map cm
            LEFT JOIN topics   t ON t.subject = cm.subject
                                AND (LOWER(t.name) = LOWER(cm.topic) OR {placeholders_t})
            LEFT JOIN concepts c ON c.subject = cm.subject
                                AND (LOWER(c.topic) = LOWER(cm.topic) OR {placeholders_c})
            WHERE cm.subject = ?
              AND ({placeholders_cm})
            LIMIT 1
        """
        # Build the parameters in the same order as placeholders appear:
        params = (
            like_variants +  # for t.name LIKE
            like_variants +  # for c.topic LIKE
            [subject] +
            like_variants    # for cm.topic LIKE
        )
        cursor.execute(sql_join, params)
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
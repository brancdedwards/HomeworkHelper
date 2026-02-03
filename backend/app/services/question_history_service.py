"""
Question History Service

Tracks all generated questions to prevent repetition across sessions.
Implements cooldown periods and usage analytics.
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from backend.db.session import get_db
from backend.app.core.logging_config import log_prompt_and_response


def normalize_question_text(question_text: str) -> str:
    """
    Normalize question text for consistent hashing.
    - Lowercase
    - Strip whitespace
    - Remove extra spaces
    """
    return " ".join(question_text.lower().strip().split())


def hash_question(question_text: str) -> str:
    """
    Generate SHA256 hash of normalized question text.
    This creates a unique fingerprint for each question.
    """
    normalized = normalize_question_text(question_text)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def is_question_recently_used(question_hash: str, cooldown_days: int = 7) -> bool:
    """
    Check if a question was shown recently (within cooldown period).

    Args:
        question_hash: SHA256 hash of the question
        cooldown_days: Minimum days before question can be reused (default: 7)

    Returns:
        True if question was shown within cooldown period, False otherwise
    """
    with get_db() as db:
        cutoff_date = (datetime.now() - timedelta(days=cooldown_days)).isoformat()

        row = db.execute("""
            SELECT last_shown_at
            FROM question_history
            WHERE question_hash = ?
        """, (question_hash,)).fetchone()

        if not row or not row['last_shown_at']:
            # Question never shown or doesn't exist
            return False

        last_shown = row['last_shown_at']
        return last_shown > cutoff_date


def record_question_usage(question_data: Dict[str, Any]) -> bool:
    """
    Record or update a question in the history database.
    If question exists, updates last_shown_at and times_shown.
    If new, inserts a new record.

    Args:
        question_data: Dict with keys:
            - subject (str): 'grammar' or 'reading'
            - topic (str): Topic name
            - category (str): Category name
            - question (str): Question text
            - correct_answer (str): The correct answer
            - options (list): All answer options
            - explanation (str): Explanation text
            - passage_text (str, optional): For reading comprehension

    Returns:
        True if successfully recorded, False otherwise
    """
    try:
        question_text = question_data['question']
        question_hash_value = hash_question(question_text)

        with get_db() as db:
            # Check if question already exists
            existing = db.execute("""
                SELECT id, times_shown
                FROM question_history
                WHERE question_hash = ?
            """, (question_hash_value,)).fetchone()

            now = datetime.now().isoformat()

            if existing:
                # Update existing question
                db.execute("""
                    UPDATE question_history
                    SET times_shown = times_shown + 1,
                        last_shown_at = ?
                    WHERE question_hash = ?
                """, (now, question_hash_value))
                log_prompt_and_response("question_reused", f"Question hash {question_hash_value[:16]}... shown {existing['times_shown'] + 1} times")
            else:
                # Insert new question
                db.execute("""
                    INSERT INTO question_history (
                        subject, topic, category, question_text, question_hash,
                        correct_answer, options_json, explanation, passage_text,
                        times_shown, last_shown_at, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """, (
                    question_data.get('subject', 'grammar'),
                    question_data.get('topic', ''),
                    question_data.get('category', ''),
                    question_text,
                    question_hash_value,
                    question_data.get('correct_answer', ''),
                    json.dumps(question_data.get('options', [])),
                    question_data.get('explanation', ''),
                    question_data.get('passage_text'),  # NULL for grammar
                    now,
                    now
                ))
                log_prompt_and_response("question_recorded", f"New question hash {question_hash_value[:16]}... recorded")

            db.commit()
            return True

    except Exception as e:
        log_prompt_and_response("question_history_error", f"Error recording question: {e}")
        return False


def get_question_stats(subject: Optional[str] = None) -> Dict[str, Any]:
    """
    Get statistics about question history.

    Args:
        subject: Optional subject filter ('grammar', 'reading')

    Returns:
        Dict with stats: total_questions, avg_times_shown, etc.
    """
    with get_db() as db:
        if subject:
            stats = db.execute("""
                SELECT
                    COUNT(*) as total_questions,
                    AVG(times_shown) as avg_times_shown,
                    MAX(times_shown) as max_times_shown,
                    COUNT(DISTINCT topic) as unique_topics
                FROM question_history
                WHERE subject = ?
            """, (subject,)).fetchone()
        else:
            stats = db.execute("""
                SELECT
                    COUNT(*) as total_questions,
                    AVG(times_shown) as avg_times_shown,
                    MAX(times_shown) as max_times_shown,
                    COUNT(DISTINCT topic) as unique_topics
                FROM question_history
            """).fetchone()

        return dict(stats) if stats else {}


__all__ = [
    'normalize_question_text',
    'hash_question',
    'is_question_recently_used',
    'record_question_usage',
    'get_question_stats'
]

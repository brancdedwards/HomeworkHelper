import yaml
from backend.db.session import get_db

YAML_FILE = "data/grammar_combined.yaml"

def sync_yaml_to_db():
    with open(YAML_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    inserted = 0
    with get_db() as db:
        for topic, fields in data.items():
            db.execute("""
                INSERT OR IGNORE INTO topics (name, category, question_focus, active)
                VALUES (?, ?, ?, 1)
            """, (
                topic,
                fields.get("category"),
                fields.get("question_focus")
            ))
            inserted += 1

    return inserted
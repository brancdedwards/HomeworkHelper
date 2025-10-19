import datetime
import os
import yaml
from datetime import datetime

import sqlite3
DB_PATH = "data/homework_helper.db"
# DB_PATH = os.path.join(os.path.dirname(__file__), "..", "/data/homework_helper.db")
def get_connection():
    return sqlite3.connect(DB_PATH)
YAML_PATH = "data/grammar_hints.yaml"


def sync_yaml_to_db():
    import streamlit as st
    st.write("🔍 Using database:", os.path.abspath(DB_PATH))

    """Load YAML topics and sync to SQLite, preserving dynamic metadata."""
    conn = get_connection()
    cursor = conn.cursor()
    print("🔍 Using database:", os.path.abspath(DB_PATH))
    # Load YAML
    st.write(YAML_PATH)
    with open(YAML_PATH, "r") as f:
        yaml_data = yaml.safe_load(f)

    for name, content in yaml_data.items():
        meta = content.get("meta", {})
        subject = meta.get("subject", "grammar")
        grade = meta.get("grade_level", 5)
        active = int(meta.get("active", False))
        last_seen = meta.get("last_seen_date", None)
        updated_at = datetime.now()

        cursor.execute("""
            INSERT INTO topics (name, subject, grade_level, active, last_seen_date)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                subject = excluded.subject,
                grade_level = excluded.grade_level,
                active = excluded.active,
                last_seen_date = excluded.last_seen_date,
                updated_at = excluded.updated_at
        """, (name, subject, grade, active, last_seen))

    conn.commit()
    conn.close()
    print("✅ YAML topics synced to database successfully.")

def sync_db_to_yaml():
    """Synchronize metadata from the SQLite database back to YAML files."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, subject, grade_level, active, last_seen_date FROM topics")
    rows = cursor.fetchall()

    # Group topics by subject
    subjects = {}
    for name, subject, grade_level, active, last_seen_date in rows:
        subjects.setdefault(subject, []).append({
            "name": name,
            "grade_level": grade_level,
            "active": bool(active),
            "last_seen_date": last_seen_date
        })

    for subject, topics in subjects.items():
        yaml_path = os.path.join("data", f"{subject}_hints.yaml")
        if os.path.exists(yaml_path):
            with open(yaml_path, "r") as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

        for topic in topics:
            name = topic["name"]
            if name not in data:
                data[name] = {
                    "definition": "Pending definition.",
                    "examples": [],
                    "link": "",
                    "_meta": {}
                }
            meta = data[name].setdefault("_meta", {})
            meta.update({
                "grade_level": topic["grade_level"],
                "active": topic["active"],
                "last_seen_date": topic["last_seen_date"],
                "subject": subject
            })

        with open(yaml_path, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False)

    conn.close()
    print("✅ Database topics synced to YAML files successfully.")

def update_topics(parsed_topics, yaml_dir="data/"):
    """
    Synchronizes parsed newsletter topics with their respective YAML files.
    Creates or updates entries automatically using the _meta structure.
    """
    os.makedirs(yaml_dir, exist_ok=True)

    for topic in parsed_topics:
        subject = topic["subject"]
        name = topic["topic"].lower().replace(" ", "_")

        yaml_path = os.path.join(yaml_dir, f"{subject}_hints.yaml")

        # Create YAML file if missing
        if not os.path.exists(yaml_path):
            with open(yaml_path, "w") as f:
                yaml.safe_dump({}, f)

        # Load existing YAML
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f) or {}

        # Ensure proper structure
        if name not in data:
            data[name] = {
                "definition": "Pending definition.",
                "examples": [],
                "link": "",
                "_meta": {
                    "active": True,
                    "grade_level": 5,
                    "last_seen_date": topic["date"],
                    "subject": subject
                }
            }
        else:
            # Update metadata section safely
            meta = data[name].setdefault("_meta", {})
            meta.update({
                "active": True,
                "last_seen_date": topic["date"],
                "subject": subject,
                "grade_level": meta.get("grade_level", 5)
            })

        # Save changes back to YAML
        with open(yaml_path, "w") as f:
            yaml.safe_dump(data, f, sort_keys=False)

if __name__ == "__main__":
    import sys
    direction = sys.argv[1] if len(sys.argv) > 1 else None

    if direction == "db_to_yaml":
        sync_db_to_yaml()
    else:
        from parser_newsletter import parse_newsletter
        text = """
        Week of 10/14/2025
        Grammar: Adverbs
        Reading: Point of View
        Math: Fractions
        """
        topics = parse_newsletter(text)
        update_topics(topics)
        sync_yaml_to_db()
        print("YAML files updated successfully.")
import datetime, os, yaml, sys, streamlit as st, sqlite3
from datetime import datetime

def normalize_db_topic(name: str) -> str:
    """Convert snake_case → space case for DB consistency."""
    return name.strip().lower().replace("_", " ")

def normalize_yaml_key(name: str) -> str:
    """Convert space case → snake_case if ever needed."""
    return name.strip().lower().replace(" ", "_")

DB_PATH = "data/homework_helper.db"
# DB_PATH = os.path.join(os.path.dirname(__file__), "..", "/data/homework_helper.db")
def get_connection():
    return sqlite3.connect(DB_PATH)
YAML_PATH = "data/grammar_combined.yaml"

def sync_topics_to_concepts():
    """
    Copy active topics from the topics table into the concepts table if not already present.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Select all active topics
    cur.execute("SELECT name, subject FROM topics")
    topics = cur.fetchall()
    inserted = 0
    skipped = 0
    for name, subject in topics:
        # Check if concept exists with same subject and topic
        cur.execute(
            "SELECT id FROM concepts WHERE subject = ? AND topic = ?",
            (subject, name)
        )
        if cur.fetchone():
            print(f"⏩ Skipped (already exists): subject='{subject}', topic='{name}'")
            skipped += 1
            continue
        # Insert new concept
        cur.execute(
            """
            INSERT INTO concepts (date_start, subject, topic, type, notes, created_at)
            VALUES (CURRENT_DATE, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (subject, name, "auto_sync", "Auto-synced from topics")
        )
        print(f"✅ Inserted: subject='{subject}', topic='{name}'")
        inserted += 1
    conn.commit()
    conn.close()
    print(f"Summary: Inserted: {inserted}, Skipped: {skipped}")



def sync_yaml_to_db():
    """
    Import grammar hints from YAML into the SQLite grammar_hints table.
    Automatically creates the table if it does not exist.
    """
    st.write("🔍 Using database:", os.path.abspath(DB_PATH))
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Ensure grammar_hints table exists
    # cur.execute("""
    #     CREATE TABLE IF NOT EXISTS grammar_hints (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         topic TEXT UNIQUE NOT NULL,
    #         definition TEXT,
    #         examples TEXT,
    #         link TEXT,
    #         category TEXT DEFAULT 'grammar',
    #         created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    #         updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    #     )
    # """)

    _YAML_PATH = "data/grammar_combined.yaml"
    with open(_YAML_PATH, "r") as f:
        hints = yaml.safe_load(f)

    # Sync to topics table
    cur.execute("SELECT name FROM topics")
    existing_topics = {row[0] for row in cur.fetchall()}

    for topic_name, details in hints.items():
        # topic_name: "adjective", "adverb", ...
        # details: dict with category, question_focus, definition, etc.
        normalized = normalize_db_topic(topic_name)
        category = normalize_db_topic(details.get("category", "")) if details.get("category") else ""
        question_focus = details.get("question_focus", "").strip()
        # examples is handled later
        if normalized not in existing_topics:
            cur.execute(
                # "INSERT INTO topics (name, subject, active, grade_level, last_seen_date, category, question_focus, example) VALUES (?, ?, 1, 5, ?, ?, ?, ?) ON CONFLICT(name) DO UPDATE SET last_seen_date = ?, category = ?, question_focus = ?, example = ?",
                "INSERT INTO topics (name, subject, active, grade_level, last_seen_date, category, question_focus, example) VALUES (?, ?, 1, 5, ?, ?, ?, ?)",

                (normalized, "grammar", datetime.now().isoformat(), category, question_focus, details.get("examples", ""))

            )

    st.write(f"Loaded {len(hints)} topics from YAML")

    inserted, updated, skipped = 0, 0, 0

    for topic_name, details in hints.items():
        normalized = normalize_db_topic(topic_name)
        definition = details.get("definition", "")
        raw_examples = details.get("examples", [])
        if isinstance(raw_examples, str):
            raw_examples = [raw_examples]
        elif not isinstance(raw_examples, list):
            raw_examples = []

        examples = " ".join(e.replace("\r", "").replace("\n", " ").strip() for e in raw_examples)
        link = details.get("link", "")
        now = datetime.now().isoformat()

        # Check if topic exists
        cur.execute("SELECT id FROM grammar_hints WHERE topic = ?", (normalized,))
        result = cur.fetchone()

        if result:
            # Update existing entry
            cur.execute("""
                UPDATE grammar_hints
                SET definition = ?, examples = ?, link = ?, updated_at = ?
                WHERE id = ?
            """, (definition, examples, link, now, result[0]))
            updated += 1
            print(f"🔄 Updated: {topic_name}")
        else:
            # Insert new entry
            cur.execute("""
                INSERT INTO grammar_hints (topic, definition, examples, link)
                VALUES (?, ?, ?, ?)
            """, (normalized, definition, examples, link))
            inserted += 1
            print(f"✅ Inserted: {topic_name}")

    conn.commit()
    conn.close()

    print(f"\nSummary:")
    print(f"✅ Inserted: {inserted}")
    print(f"🔄 Updated: {updated}")
    print(f"⚠️ Skipped: {skipped}")
    return hints
# Example run:
# sync_yaml_to_topics("data/grammar_combined.yaml", "data/homework_helper.db")

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
        name = topic["topic"].lower().replace("_", " ")

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
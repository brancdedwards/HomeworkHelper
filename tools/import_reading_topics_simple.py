#!/usr/bin/env python3
"""
Simple Reading Topics Importer
Imports reading topics from CSV and distributes them evenly across 4 categories
"""

import csv
import sqlite3
import sys
from pathlib import Path

# Categories to cycle through
CATEGORIES = [
    'main_idea_theme',
    'inference_conclusions',
    'vocabulary_in_context',
    'text_structure_purpose'
]

def import_reading_topics(csv_path: str, db_path: str):
    """Import reading topics from CSV into database"""

    # Read CSV
    topics = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            topics.append(row['topic_name'])

    print(f"Found {len(topics)} topics in CSV")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Import topics, cycling through categories
    imported = 0
    for i, topic_name in enumerate(topics):
        category = CATEGORIES[i % len(CATEGORIES)]

        try:
            cursor.execute("""
                INSERT INTO topics (name, subject, category, active, grade_level)
                VALUES (?, 'reading', ?, 1, 5)
            """, (topic_name, category))
            imported += 1
            print(f"✓ Imported: {topic_name} → {category}")
        except sqlite3.IntegrityError:
            print(f"✗ Skipped (duplicate): {topic_name}")

    conn.commit()
    conn.close()

    print(f"\n✅ Successfully imported {imported}/{len(topics)} topics")

    # Show distribution
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, COUNT(*)
        FROM topics
        WHERE subject='reading' AND active=1
        GROUP BY category
        ORDER BY category
    """)

    print("\nCategory Distribution:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} topics")

    conn.close()

if __name__ == '__main__':
    csv_path = Path(__file__).parent.parent / 'data' / 'imports' / 'reading_topics.csv'
    db_path = Path(__file__).parent.parent / 'backend' / 'db' / 'homeworkhelper.db'

    import_reading_topics(str(csv_path), str(db_path))

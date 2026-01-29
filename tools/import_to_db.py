#!/usr/bin/env python3
"""
Import Topics to Database
Imports reviewed topics from JSON file to the SQLite database

Usage:
    python tools/import_to_db.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db.session import get_db


def normalize_category(category: str) -> str:
    """Normalize category to match database format"""
    # Convert to lowercase and replace spaces with underscores
    return category.lower().replace(' ', '_')


def import_topics_to_db(topics: list) -> tuple[int, int]:
    """Import topics to database

    Returns:
        Tuple of (inserted_count, skipped_count)
    """
    inserted = 0
    skipped = 0

    with get_db() as db:
        for topic in topics:
            # Check if topic already exists
            existing = db.execute(
                "SELECT id FROM topics WHERE LOWER(name) = LOWER(?) AND subject = 'grammar'",
                (topic['name'],)
            ).fetchone()

            if existing:
                print(f"⚠️  Skipping '{topic['name']}' - already exists")
                skipped += 1
                continue

            # Normalize category to match DB format
            normalized_category = normalize_category(topic['category'])

            # Insert new topic
            try:
                db.execute("""
                    INSERT INTO topics (
                        name,
                        subject,
                        category,
                        question_focus,
                        prompt_template,
                        example,
                        active,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    topic['name'],
                    'grammar',
                    normalized_category,
                    topic.get('question_focus', ''),  # Use get() for backwards compatibility
                    topic['prompt_template'],
                    topic['example'],
                    1,  # active
                    datetime.now().isoformat()
                ))

                print(f"✓ Imported: {topic['name']} ({topic['category']})")
                inserted += 1

            except Exception as e:
                print(f"❌ Error importing '{topic['name']}': {e}")
                skipped += 1

    return inserted, skipped


def main():
    review_file = Path("data/imports/topics_review.json")

    if not review_file.exists():
        print("❌ Review file not found!")
        print("Run: python tools/import_topics.py <csv_file> first")
        sys.exit(1)

    # Load topics
    with open(review_file, 'r') as f:
        topics = json.load(f)

    print(f"\n📚 Found {len(topics)} topics to import")
    confirm = input("Continue with import? (y/n): ")

    if confirm.lower() != 'y':
        print("Import cancelled")
        return

    print("\nImporting topics to database...\n")

    # Import to database
    inserted, skipped = import_topics_to_db(topics)

    print(f"\n{'='*60}")
    print(f"✅ Import complete!")
    print(f"   Inserted: {inserted}")
    print(f"   Skipped:  {skipped}")
    print(f"{'='*60}\n")

    # Archive the review file
    archive_path = Path(f"data/imports/topics_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    review_file.rename(archive_path)
    print(f"📁 Review file archived to: {archive_path}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nImport cancelled")

#!/usr/bin/env python3
"""
Topic Import Pipeline
Reads CSV of grammar topics and generates metadata using Claude API

Usage:
    python tools/import_topics.py data/imports/grammar_topics.csv
"""

import csv
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, validator
from anthropic import Anthropic
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.core.settings import settings

# Valid categories from the database
VALID_CATEGORIES = [
    "Grammar Mechanics",
    "Literary Devices",
    "Parts Of Speech",
    "Punctuation",
    "Sentence Structure",
    "Sentence Type",
    "Vocabulary",
    "Writing Quality"
]

GRADE_LEVELS = ["3rd grade", "4th grade", "5th grade", "6th grade"]


class TopicMetadata(BaseModel):
    """Structured metadata for a grammar topic"""
    name: str = Field(..., description="The grammar topic name")
    category: str = Field(..., description="Category from the valid list")
    prompt_template: str = Field(..., description="Template for generating questions")
    example: str = Field(..., description="Example question with answer")
    grade_level: str = Field(default="5th grade", description="Target grade level")
    source: Optional[str] = Field(None, description="Source of the topic (newsletter date, etc)")

    @validator('category')
    def validate_category(cls, v):
        if v not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of: {VALID_CATEGORIES}")
        return v

    @validator('grade_level')
    def validate_grade(cls, v):
        if v not in GRADE_LEVELS:
            raise ValueError(f"Grade level must be one of: {GRADE_LEVELS}")
        return v


class TopicGenerator:
    """Generates topic metadata using Claude API"""

    def __init__(self):
        self.client = Anthropic(api_key=settings.CLAUDE_API_KEY)
        self.model = settings.LLM_MODEL

    def generate_metadata(self, topic_name: str, source: str = None, notes: str = None) -> TopicMetadata:
        """Generate metadata for a single topic using Claude"""

        prompt = self._build_prompt(topic_name, source, notes)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for more consistent output
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse JSON response
            content = response.content[0].text

            # Extract JSON from response (in case there's extra text)
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                data = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")

            # Add source if provided
            if source:
                data['source'] = source

            # Validate and create TopicMetadata
            metadata = TopicMetadata(**data)

            # Self-validation
            if not self._validate_metadata(metadata):
                print(f"⚠️  Warning: Generated metadata for '{topic_name}' may need review")

            return metadata

        except Exception as e:
            print(f"❌ Error generating metadata for '{topic_name}': {e}")
            raise

    def _build_prompt(self, topic_name: str, source: str = None, notes: str = None) -> str:
        """Build the prompt for Claude with strict guardrails"""

        notes_section = f"\nAdditional context: {notes}" if notes else ""

        return f"""You are a 5th grade grammar curriculum expert. Generate question metadata for the following grammar topic.

Topic: {topic_name}{notes_section}

Requirements:
1. Category MUST be exactly one of: {', '.join(VALID_CATEGORIES)}
2. Questions must be age-appropriate for 5th grade
3. Use concrete, relatable examples (kids, school, pets, sports, etc.)
4. Prompt template should guide question generation with placeholders like {{word}}, {{sentence}}, {{context}}
5. Example must include the question AND the correct answer
6. Keep explanations simple and clear (1-2 sentences max)
7. Focus on practical usage, not abstract grammar rules

Output ONLY valid JSON in this exact format:
{{
    "name": "{topic_name}",
    "category": "one of the valid categories",
    "prompt_template": "Template for generating questions about this topic. Use placeholders like {{word}} or {{sentence}}.",
    "example": "Example question: [full question text]\\nCorrect answer: [answer]\\nExplanation: [why this is correct]",
    "grade_level": "5th grade"
}}

IMPORTANT:
- Respond with ONLY the JSON object, no other text
- Ensure the category exactly matches one from the list above
- Make sure the example demonstrates the topic clearly"""

    def _validate_metadata(self, metadata: TopicMetadata) -> bool:
        """Self-validation check"""

        # Basic checks
        if len(metadata.prompt_template) < 20:
            return False

        if len(metadata.example) < 30:
            return False

        if metadata.category not in VALID_CATEGORIES:
            return False

        # Check that example contains key elements
        example_lower = metadata.example.lower()
        if 'answer' not in example_lower and 'correct' not in example_lower:
            return False

        return True


def read_topics_csv(csv_path: Path) -> List[Dict[str, str]]:
    """Read topics from CSV file"""
    topics = []

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip empty rows or header examples
            if row.get('topic_name') and not row['topic_name'].startswith('#'):
                topics.append(row)

    return topics


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/import_topics.py <csv_file>")
        print("Example: python tools/import_topics.py data/imports/grammar_topics.csv")
        sys.exit(1)

    csv_path = Path(sys.argv[1])

    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)

    print(f"📖 Reading topics from: {csv_path}")
    topics = read_topics_csv(csv_path)
    print(f"✓ Found {len(topics)} topics to process\n")

    # Initialize generator
    generator = TopicGenerator()

    # Generate metadata for each topic
    results = []
    failed = []

    for i, topic in enumerate(topics, 1):
        topic_name = topic['topic_name']
        source = topic.get('source', '')
        notes = topic.get('notes', '')

        print(f"[{i}/{len(topics)}] Generating metadata for: {topic_name}")

        try:
            metadata = generator.generate_metadata(topic_name, source, notes)
            results.append(metadata.dict())
            print(f"  ✓ Category: {metadata.category}")
            print(f"  ✓ Grade: {metadata.grade_level}")
            print()
        except Exception as e:
            print(f"  ❌ Failed: {e}\n")
            failed.append(topic_name)

    # Save results to review file
    output_path = Path("data/imports/topics_review.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"✅ Successfully generated metadata for {len(results)} topics")
    if failed:
        print(f"❌ Failed to generate {len(failed)} topics: {', '.join(failed)}")
    print(f"\n📄 Review file saved to: {output_path}")
    print(f"\nNext steps:")
    print(f"1. Review the generated metadata in {output_path}")
    print(f"2. Edit any topics that need changes")
    print(f"3. Run: python tools/review_topics.py")
    print(f"4. Run: python tools/import_to_db.py")
    print('='*60)


if __name__ == "__main__":
    main()

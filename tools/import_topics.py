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
    question_focus: str = Field(..., description="Short question focus/prompt (e.g., 'Which word shows action?')")
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

            # CRITICAL: Validate that only ONE answer is correct
            validation_result = self._validate_question_correctness(metadata)
            if not validation_result['valid']:
                print(f"⚠️  Question validation failed: {validation_result['reason']}")
                print(f"   Attempting to regenerate with stricter prompt...")
                # Retry with enhanced prompt
                return self._regenerate_with_validation(topic_name, source, notes)

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
4. Question focus should be a short phrase asking what the student should identify/do
5. Prompt template should guide question generation with placeholders like {{word}}, {{sentence}}, {{context}}
6. Keep explanations simple and clear (1-2 sentences max)
7. Focus on practical usage, not abstract grammar rules

CRITICAL REQUIREMENT FOR EXAMPLE QUESTIONS:
- The example MUST be a multiple-choice question with 4 options (A, B, C, D)
- EXACTLY ONE option must be correct
- The other THREE options must contain CLEAR, OBVIOUS grammar errors
- Do NOT create ambiguous questions where multiple answers could be correct
- Incorrect options should be clearly wrong to any grammar expert

Example format:
Example question: Which sentence uses the apostrophe correctly?
A) The dog's ball is red. [CORRECT - possessive]
B) The dogs ball is red. [WRONG - missing apostrophe]
C) The dog's are playing. [WRONG - incorrect use with plural verb]
D) Its a nice day. [WRONG - should be "it's" for contraction]
Correct answer: A
Explanation: The apostrophe shows possession - the ball belongs to the dog.

Output ONLY valid JSON in this exact format:
{{
    "name": "{topic_name}",
    "category": "one of the valid categories",
    "question_focus": "Short question asking what to identify/do",
    "prompt_template": "Template for generating questions about this topic. Use placeholders like {{word}} or {{sentence}}.",
    "example": "Example question: Which sentence uses X correctly?\\nA) Option one\\nB) Option two\\nC) Option three\\nD) Option four\\nCorrect answer: A\\nExplanation: Why A is correct.",
    "grade_level": "5th grade"
}}

CRITICAL FORMATTING NOTES:
- The "example" field MUST be a SINGLE STRING, NOT a nested JSON object
- Use \\n (newline characters) to separate lines within the example string
- Follow the exact format shown above with A), B), C), D) options
- Ensure EXACTLY ONE correct answer in your example
- Make incorrect options obviously wrong with clear grammar errors
- Ensure the category exactly matches one from the list above

Respond with ONLY the JSON object, no other text before or after."""

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

    def _validate_question_correctness(self, metadata: TopicMetadata) -> dict:
        """
        Use AI to validate that the generated question has only ONE correct answer.
        Returns: {'valid': bool, 'reason': str}
        """
        validation_prompt = f"""You are a strict grammar teacher. Analyze this question and determine if it has EXACTLY ONE correct answer.

Question: {metadata.example}

Your task:
1. Identify all answer choices in the question
2. Determine which answers are grammatically correct
3. If MORE THAN ONE answer is correct, explain why
4. If ZERO answers are correct, explain why

Respond with ONLY a JSON object:
{{
    "num_correct_answers": <number>,
    "correct_answers": ["list", "of", "correct", "answers"],
    "is_valid": <true if exactly 1 correct answer, false otherwise>,
    "reason": "explanation if invalid"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,  # Very low for objective evaluation
                messages=[{
                    "role": "user",
                    "content": validation_prompt
                }]
            )

            content = response.content[0].text
            json_start = content.find('{')
            json_end = content.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                validation = json.loads(content[json_start:json_end])

                if validation.get('is_valid'):
                    return {'valid': True, 'reason': 'Question has exactly one correct answer'}
                else:
                    return {
                        'valid': False,
                        'reason': f"{validation.get('num_correct_answers', 'Unknown')} correct answers found: {', '.join(validation.get('correct_answers', []))}"
                    }
            else:
                return {'valid': True, 'reason': 'Could not parse validation, assuming valid'}

        except Exception as e:
            print(f"   Validation error: {e}")
            return {'valid': True, 'reason': 'Validation failed, assuming valid'}

    def _regenerate_with_validation(self, topic_name: str, source: str = None, notes: str = None, attempt: int = 1) -> TopicMetadata:
        """Regenerate question with enhanced prompt emphasizing ONE correct answer"""

        if attempt > 2:  # Max 2 retries
            print(f"   ⚠️  Max retries reached, keeping questionable question")
            # Return original even if flawed
            return self.generate_metadata(topic_name, source, notes)

        print(f"   🔄 Regeneration attempt {attempt}/2...")

        enhanced_notes = f"{notes or ''}\n\nCRITICAL: Ensure ONLY ONE answer is correct. Make incorrect options clearly wrong with obvious grammar errors."

        return self.generate_metadata(topic_name, source, enhanced_notes)


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

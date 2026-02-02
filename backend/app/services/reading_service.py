"""
Reading Comprehension Service

Generates reading passages and comprehension questions for 4 question types:
1. Main Idea & Theme
2. Inference & Conclusions
3. Vocabulary in Context
4. Text Structure & Purpose
"""

from backend.app.services.llm_service import generate_mcq_question
from backend.app.services.topic_service import get_topic_data
from backend.app.core.logging_config import log_prompt_and_response
from backend.app.core.settings import Settings
from anthropic import Anthropic
import json
import random

settings = Settings()
client = Anthropic(api_key=settings.CLAUDE_API_KEY)


# Reading comprehension question type prompts
READING_QUESTION_PROMPTS = {
    'main_idea_theme': """Based on this passage, create a question asking students to identify the main idea or central theme.

CRITICAL REQUIREMENTS:
- The correct answer should clearly state the central message or main point of the passage
- The THREE incorrect answers should be:
  * Supporting details (important but not the main idea)
  * Minor points mentioned in passing
  * Misinterpretations or overgeneralizations
- Make sure ONLY ONE answer correctly identifies the main idea
- Incorrect options should be clearly wrong to someone who understood the passage

Example question format:
"What is the main idea of this passage?"
A) [supporting detail - WRONG]
B) [correct main idea - CORRECT]
C) [minor point - WRONG]
D) [misinterpretation - WRONG]""",

    'inference_conclusions': """Create a question requiring students to make an inference or draw a conclusion that is NOT directly stated in the passage.

CRITICAL REQUIREMENTS:
- The correct answer should be a logical deduction that can be made from the passage
- The THREE incorrect answers should be:
  * Claims not supported by the passage
  * Conclusions that contradict the passage
  * Surface-level readings that miss deeper meaning
- The inference must require reading between the lines
- Make sure ONLY ONE answer is a valid inference

Example question format:
"Based on the passage, what can you infer about...?"
A) [unsupported claim - WRONG]
B) [contradicts passage - WRONG]
C) [valid inference - CORRECT]
D) [surface reading - WRONG]""",

    'vocabulary_in_context': """Create a question about the meaning of a word as used in the passage.

CRITICAL REQUIREMENTS:
- Select a word from the passage that has multiple meanings
- Include the sentence containing the word in the question
- The correct answer should match how the word is used in THIS passage
- The THREE incorrect answers should be:
  * Valid definitions of the word, but wrong in this context
  * Related words that don't quite fit
  * Common misinterpretations
- Make sure ONLY ONE answer fits the context

Example question format:
"In the sentence '[quote from passage]', what does the word 'X' mean?"
A) [definition 1, wrong in context - WRONG]
B) [correct contextual meaning - CORRECT]
C) [definition 2, wrong in context - WRONG]
D) [related word - WRONG]""",

    'text_structure_purpose': """Create a question about how the passage is organized or why the author wrote it.

CRITICAL REQUIREMENTS:
- Ask about the passage's structure (chronological, compare/contrast, problem/solution, cause/effect, descriptive)
  OR ask about the author's purpose (to inform, to persuade, to entertain, to explain)
- The correct answer should accurately identify the structure or purpose
- The THREE incorrect answers should be:
  * Other valid structures/purposes that don't match this passage
  * Partially correct but incomplete descriptions
  * Common misidentifications
- Make sure ONLY ONE answer correctly identifies the structure/purpose

Example question format:
"How is this passage organized?" OR "What is the author's main purpose?"
A) [wrong structure/purpose - WRONG]
B) [correct structure/purpose - CORRECT]
C) [partially correct - WRONG]
D) [common misidentification - WRONG]"""
}


def generate_passage(topic: str, category: str, grade_level: str = "5th grade", length: str = "medium") -> dict:
    """
    Generate a reading passage using Claude.

    Args:
        topic: The topic/subject of the passage
        category: Reading category (main_idea_theme, inference_conclusions, etc.)
        grade_level: Target reading level (default: 5th grade)
        length: Passage length (short=150-200, medium=250-350, long=400-500 words)

    Returns:
        dict with passage_text, word_count, and estimated_grade_level
    """
    length_specs = {
        "short": (150, 200, "a brief passage"),
        "medium": (250, 350, "a moderate-length passage"),
        "long": (400, 500, "a longer, more detailed passage")
    }

    min_words, max_words, length_desc = length_specs.get(length, length_specs["medium"])

    # Determine passage style based on category
    category_styles = {
        'main_idea_theme': "an informational article or narrative story with a clear central message",
        'inference_conclusions': "a passage rich in details that requires reading between the lines",
        'vocabulary_in_context': "a passage using varied and interesting vocabulary",
        'text_structure_purpose': "a passage with clear organizational structure"
    }

    style_guidance = category_styles.get(category, "an engaging passage")

    # Variety instructions to avoid repetitive content
    variety_instructions = """
CRITICAL - CREATE UNIQUE, ENGAGING CONTENT:
- Use DIVERSE subjects and settings (avoid overused examples)
- Create vivid, specific scenarios that feel fresh and interesting
- Use creative details that would engage 5th graders
- Avoid clichéd topics or predictable narratives
- Make every passage feel unique and worth reading
"""

    prompt = f"""You are an expert in children's literature and education. Generate {length_desc} suitable for {grade_level} students.

Topic: {topic}
Target reading level: {grade_level}
Passage style: {style_guidance}

Requirements:
- Length: {min_words}-{max_words} words
- Reading level: Appropriate for {grade_level} (Flesch-Kincaid Grade Level 4-6)
- Engaging and age-appropriate content
- Clear structure with beginning, middle, and end
- Include vivid details and varied vocabulary
- Educational and informative
- Write in complete paragraphs (2-4 paragraphs total)

{variety_instructions}

Return ONLY the passage text. Do not include a title, do not add any preamble or commentary.
Just write the passage itself."""

    try:
        response = client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=800,
            temperature=0.7,  # Higher for creative passage generation
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        passage_text = response.content[0].text.strip()
        word_count = len(passage_text.split())

        log_prompt_and_response("passage_generation", f"Topic: {topic}, Words: {word_count}")

        return {
            "passage_text": passage_text,
            "word_count": word_count,
            "grade_level": grade_level,
            "topic": topic
        }

    except Exception as e:
        log_prompt_and_response("passage_generation_error", str(e))
        raise ValueError(f"Failed to generate passage: {e}")


def generate_reading_question(passage: dict, category: str, difficulty: str = "normal", style: str = "default") -> dict:
    """
    Generate a reading comprehension question about a passage.

    Args:
        passage: Dict with passage_text, topic, etc.
        category: Question type (main_idea_theme, inference_conclusions, etc.)
        difficulty: Question difficulty level
        style: Question style (default, challenge, etc.)

    Returns:
        dict with question, options, correct_answer, explanation, and passage fields
    """
    passage_text = passage.get("passage_text", "")
    topic = passage.get("topic", "")

    # Get category-specific prompt
    category_prompt = READING_QUESTION_PROMPTS.get(
        category,
        READING_QUESTION_PROMPTS['main_idea_theme']  # Default
    )

    enhanced_prompt = f"""You are a reading comprehension expert creating questions for {passage.get('grade_level', '5th grade')} students.

PASSAGE:
{passage_text}

TASK: {category_prompt}

CRITICAL OUTPUT REQUIREMENTS:
- Generate EXACTLY ONE multiple-choice question with EXACTLY 4 options (A, B, C, D)
- EXACTLY ONE option must be correct
- The other THREE options must be clearly incorrect
- Each option should be concise (1-2 sentences maximum)
- Include a brief explanation (2-3 sentences) of why the correct answer is right

Output ONLY valid JSON in this exact format:
{{
    "prompt": "Your question here?",
    "options": [
        {{"text": "Option A", "is_correct": false}},
        {{"text": "Option B", "is_correct": true}},
        {{"text": "Option C", "is_correct": false}},
        {{"text": "Option D", "is_correct": false}}
    ],
    "explanation": "Brief explanation of the correct answer.",
    "topic": "{topic}",
    "subject": "reading"
}}

Remember: ONLY ONE is_correct should be true. Output ONLY the JSON, nothing else."""

    try:
        response = client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=1000,
            temperature=0.3,  # Lower for consistent question generation
            messages=[{
                "role": "user",
                "content": enhanced_prompt
            }]
        )

        content = response.content[0].text.strip()

        # Extract JSON from response
        json_start = content.find('{')
        json_end = content.rfind('}') + 1

        if json_start >= 0 and json_end > json_start:
            json_content = content[json_start:json_end]
            question_data = json.loads(json_content)

            # Add passage fields
            question_data['passage_text'] = passage_text
            question_data['passage_title'] = passage.get('title')
            question_data['passage_source'] = passage.get('source')
            question_data['passage_grade_level'] = passage.get('grade_level')

            # Ensure subject is set
            question_data['subject'] = 'reading'
            question_data['topic'] = topic

            # Extract correct answer text
            correct_answer = next(
                (opt['text'] for opt in question_data['options'] if opt.get('is_correct')),
                None
            )

            return {
                'topic': topic,
                'category': category,
                'question': question_data['prompt'],
                'options': [opt['text'] for opt in question_data['options']],
                'correct_answer': correct_answer,
                'explanation': question_data.get('explanation', ''),
                'passage_text': passage_text,
                'passage_title': passage.get('title'),
                'passage_source': passage.get('source'),
                'passage_grade_level': passage.get('grade_level')
            }
        else:
            raise ValueError("No valid JSON found in response")

    except Exception as e:
        log_prompt_and_response("reading_question_error", str(e))
        raise ValueError(f"Failed to generate reading question: {e}")


def generate_reading_session(num_questions: int, category: str = None, difficulty: str = "normal", style: str = "default", questions_per_passage: int = 3):
    """
    Generate a reading comprehension practice session with N questions.
    Generates multiple questions per passage for efficiency and variety.

    Args:
        num_questions: Total number of questions to generate
        category: Specific reading category, or None for random mix
        difficulty: Question difficulty level
        style: Question style
        questions_per_passage: Number of questions to generate per passage (default: 3)

    Returns:
        List of question dicts with passage, question, options, etc.
    """
    from backend.db.session import get_db

    # Normalize category
    if category:
        category_normalized = category.lower().replace(' ', '_')
    else:
        category_normalized = None

    # Fetch active reading topics from database
    with get_db() as db:
        if category_normalized:
            rows = db.execute("""
                SELECT name, category FROM topics
                WHERE LOWER(category) = LOWER(?)
                  AND active = 1
                  AND subject = 'reading'
            """, (category_normalized,)).fetchall()
        else:
            rows = db.execute("""
                SELECT name, category FROM topics
                WHERE active = 1
                  AND subject = 'reading'
            """).fetchall()

        topics = [dict(row) for row in rows]

    if not topics:
        raise ValueError(f"No active reading topics found for category: {category}" if category else "No active reading topics found")

    # Calculate how many passages we need
    num_passages = (num_questions + questions_per_passage - 1) // questions_per_passage

    # Select topics for passages (one topic per passage)
    available_count = len(topics)
    if available_count < num_passages:
        selected_passage_topics = random.choices(topics, k=num_passages)
    else:
        selected_passage_topics = random.sample(topics, num_passages)

    # Generate questions with passages - with duplicate prevention
    questions = []
    seen_passages = set()  # Track passage beginnings to prevent duplicates
    seen_questions = set()  # Track question text to prevent duplicates
    all_categories = list(READING_QUESTION_PROMPTS.keys())
    max_passage_retries = 2
    max_question_retries = 3

    for passage_idx, passage_topic_data in enumerate(selected_passage_topics):
        passage_generated = False

        for passage_attempt in range(max_passage_retries):
            try:
                topic_name = passage_topic_data['name']

                # Generate ONE passage
                passage = generate_passage(
                    topic=topic_name,
                    category=passage_topic_data['category'],
                    grade_level="5th grade",
                    length="medium"
                )

                # Check if we've seen a very similar passage (first 100 chars)
                passage_signature = passage['passage_text'][:100].lower().strip()
                if passage_signature in seen_passages:
                    log_prompt_and_response("duplicate_passage_detected", f"Retry {passage_attempt + 1}: Similar passage for {topic_name}")
                    continue

                seen_passages.add(passage_signature)
                passage_generated = True

                # Generate MULTIPLE questions about this passage
                # Each question uses a different category (main idea, inference, vocab, structure)
                questions_for_this_passage = min(
                    questions_per_passage,
                    num_questions - len(questions)  # Don't exceed requested total
                )

                for q_idx in range(questions_for_this_passage):
                    question_generated = False

                    for question_attempt in range(max_question_retries):
                        try:
                            # Cycle through different question types for variety
                            question_category = all_categories[q_idx % len(all_categories)]

                            # Generate question
                            question = generate_reading_question(
                                passage=passage,
                                category=question_category,
                                difficulty=difficulty,
                                style=style
                            )

                            question_text = question['question'].lower().strip()

                            # Check for duplicate question
                            if question_text in seen_questions:
                                log_prompt_and_response("duplicate_reading_question", f"Retry {question_attempt + 1}: Duplicate question")
                                continue

                            seen_questions.add(question_text)
                            questions.append(question)
                            question_generated = True
                            break

                        except Exception as e:
                            log_prompt_and_response("reading_question_error", f"Attempt {question_attempt + 1}, Error: {e}")
                            continue

                    if not question_generated:
                        log_prompt_and_response("question_generation_failed", f"Failed after {max_question_retries} attempts")

                    # Stop if we've generated enough questions
                    if len(questions) >= num_questions:
                        break

                # Stop if we've generated enough questions
                if len(questions) >= num_questions:
                    break

                break  # Passage was successfully generated, move to next

            except Exception as e:
                log_prompt_and_response("reading_session_error", f"Topic: {passage_topic_data['name']}, Attempt: {passage_attempt + 1}, Error: {e}")
                continue

        if not passage_generated:
            log_prompt_and_response("passage_generation_failed", f"Failed to generate unique passage for {passage_topic_data['name']} after {max_passage_retries} attempts")

    if not questions:
        raise ValueError("Failed to generate any reading questions")

    return questions


__all__ = [
    'generate_passage',
    'generate_reading_question',
    'generate_reading_session',
    'READING_QUESTION_PROMPTS'
]

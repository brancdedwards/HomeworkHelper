from backend.app.services.llm_service import generate_mcq_question
from backend.app.services.topic_service import get_topic_data
from backend.app.core.logging_config import log_prompt_and_response
from backend.app.services.prompt_templates import get_style_template

# Service layer for generating grammar questions.
# This layer enhances legacy question generation by incorporating detailed topic metadata,
# such as definitions and examples, to create clearer and more informative prompts for the LLM.
# It focuses on producing age-appropriate, well-structured multiple-choice questions with specific constraints.

# Supported styles include: default, challenge, socratic, friendly, direct
# Style behavior is controlled by prompt_templates.get_style_template()
def generate_grammar_question(topic: str, subject: str = "grammar", difficulty: str = "normal", style: str = "default"):
    topic_data = get_topic_data(topic, subject)
    if not topic_data:
        raise ValueError(f"No topic data found for topic '{topic}'")

    style_block = get_style_template(style)
    difficulty_text = difficulty.capitalize()

    question_focus = topic_data.get("question_focus", "Create a clear grammar question.")
    prompt_template = topic_data.get("prompt_template", "")
    example = topic_data.get("example", "")

    # Difficulty-specific modifiers
    difficulty_modifiers = {
        'easy': """
        - Use simple, common vocabulary (5th grade level or below)
        - Keep sentences short and straightforward (8-12 words)
        - Focus on basic identification and recognition
        - Make the correct answer fairly obvious
        - Use familiar contexts (school, home, playground)
        """,
        'normal': """
        - Use age-appropriate vocabulary (5th-6th grade level)
        - Use moderate sentence complexity (10-15 words)
        - Balance recognition and application questions
        - Include some common mistake patterns as distractors
        - Use varied, engaging contexts
        """,
        'hard': """
        - Use more advanced vocabulary (6th-7th grade level)
        - Use complex sentence structures (15-20 words)
        - Focus on application, analysis, and subtle distinctions
        - Include plausible distractors that test deeper understanding
        - Require careful reading and critical thinking
        - Use less common but still grade-appropriate contexts
        """
    }

    difficulty_guidance = difficulty_modifiers.get(difficulty.lower(), difficulty_modifiers['normal'])

    # Variety instructions to prevent repetitive content
    variety_instructions = """
    CRITICAL - CREATE UNIQUE, VARIED CONTENT:
    - Use DIVERSE names (avoid: elephant, Sarah, cat, dog, pizza unless necessary for the concept)
    - Vary your question stems (don't always use "Which sentence...")
    - Use creative, interesting scenarios that 5th graders would find engaging
    - Mix up sentence topics: science, history, adventure, everyday life, nature, technology
    - Avoid clichéd examples - be imaginative!
    """

    enhanced_prompt = f"""You are an elementary‑level grammar tutor generating a multiple‑choice grammar question.

        Topic: {topic}
        Difficulty: {difficulty_text}

        Instructions:
        {prompt_template or 'N/A'}

        Examples:
        {example or 'N/A'}

        Question focus:
        {question_focus}

        Difficulty Guidelines:
        {difficulty_guidance}

        {variety_instructions}

        Style constraints:
        {style_block}

        Required output rules:
        - Produce ONE multiple‑choice question only.
        - Include exactly FOUR answer choices.
        - DO NOT include fill‑in‑the‑blank questions.
        - DO NOT reveal the correct answer in the question stem.
        - Answer choices must be short, clear, and distinct.
        - Question must match the difficulty setting above.
        - Output MUST be valid JSON with keys: question, options, answer.

        IMPORTANT:
        Return ONLY the JSON. No explanation, commentary, or helper text.
        """

    log_prompt_and_response("grammar_question", enhanced_prompt)

    return generate_mcq_question(
        topic=topic,
        subject=subject,
        prompt_instructions=enhanced_prompt,
        source_prompt=prompt_template
    )

def generate_practice_session(num_questions: int, category: str = None, difficulty: str = "normal", style: str = "default"):
    """
    Generate a practice session with N questions.
    - If category is specified, fetch topics from that category
    - If category is None, randomly select from all active topics
    - Returns list of question dicts with: topic, question, options, correct_answer, explanation
    """
    from backend.db.session import get_db
    import random

    # Normalize category from frontend format (e.g., "Grammar Mechanics")
    # to database format (e.g., "grammar_mechanics")
    if category:
        category_normalized = category.lower().replace(' ', '_')
    else:
        category_normalized = None

    # Fetch active topics
    with get_db() as db:
        if category_normalized:
            rows = db.execute("""
                SELECT name, category FROM topics
                WHERE LOWER(category) = LOWER(?)
                  AND active = 1
                  AND subject = 'grammar'
            """, (category_normalized,)).fetchall()
        else:
            rows = db.execute("""
                SELECT name, category FROM topics
                WHERE active = 1
                  AND subject = 'grammar'
            """).fetchall()

        topics = [dict(row) for row in rows]

    if not topics:
        raise ValueError(f"No active topics found for category: {category}" if category else "No active topics found")

    # Select topics for questions
    available_count = len(topics)

    if available_count < num_questions:
        # If we don't have enough unique topics, allow duplicates
        selected_topics = random.choices(topics, k=num_questions)
    else:
        # Random sample without replacement
        selected_topics = random.sample(topics, num_questions)

    # Generate questions with duplicate prevention
    # Keep generating until we have the requested number of questions
    questions = []
    seen_questions = set()  # Track question text to prevent exact duplicates
    seen_example_sentences = set()  # Track example sentences used in questions (e.g., "Marco raced through...")
    seen_overused_words = set()  # Track overused words (elephant, Sarah, etc.)
    max_retries = 3
    max_topic_iterations = num_questions * 3  # Safety limit to prevent infinite loops
    topic_iteration_count = 0

    # Keep iterating through topics until we have enough questions
    topic_pool = selected_topics.copy()

    while len(questions) < num_questions and topic_iteration_count < max_topic_iterations:
        # If we've exhausted the topic pool, reshuffle and reuse
        if not topic_pool:
            topic_pool = selected_topics.copy()
            random.shuffle(topic_pool)

        topic_data = topic_pool.pop(0)
        topic_iteration_count += 1
        question_generated = False

        for attempt in range(max_retries):
            try:
                result = generate_grammar_question(
                    topic=topic_data['name'],
                    subject='grammar',
                    difficulty=difficulty,
                    style=style
                )

                question_text = result.question.prompt.lower().strip()

                # Check for duplicate question text (exact match)
                if question_text in seen_questions:
                    log_prompt_and_response("duplicate_question_detected", f"Retry {attempt + 1}: Duplicate question for {topic_data['name']}")
                    continue

                # Check for duplicate sentence examples (sentences in quotes)
                # This catches when Claude uses the same example sentence with slightly different question wording
                import re
                sentences_in_question = re.findall(r"'([^']+)'", question_text)
                if sentences_in_question:
                    example_sentence = sentences_in_question[0][:50]  # First 50 chars of example sentence
                    if example_sentence in seen_example_sentences:
                        log_prompt_and_response("duplicate_sentence_example", f"Retry {attempt + 1}: Reusing sentence example '{example_sentence[:30]}...' in {topic_data['name']}")
                        continue
                    seen_example_sentences.add(example_sentence)

                # Check for overused words (elephant, Sarah, etc.)
                overused_words = ['elephant', 'sarah', 'dog', 'cat', 'pizza', 'marco']
                question_lower = question_text.lower()
                used_word = None

                for word in overused_words:
                    if word in question_lower:
                        # Allow if we haven't used this word yet
                        if word not in seen_overused_words:
                            seen_overused_words.add(word)
                            used_word = word
                            break
                        else:
                            # Already used this word, try regenerating
                            log_prompt_and_response("overused_word_detected", f"Retry {attempt + 1}: '{word}' overused in {topic_data['name']}")
                            used_word = None
                            break

                # If we found an overused word that's already been used, retry
                if used_word is None and any(word in question_lower for word in overused_words if word in seen_overused_words):
                    continue

                # Question is unique - add it
                seen_questions.add(question_text)

                # Extract correct answer
                correct_answer = next((opt.text for opt in result.question.options if opt.is_correct), None)

                questions.append({
                    "topic": result.source_topic,
                    "category": topic_data['category'],
                    "question": result.question.prompt,
                    "options": [opt.text for opt in result.question.options],
                    "correct_answer": correct_answer,
                    "explanation": result.question.explanation
                })

                question_generated = True
                break

            except Exception as e:
                # Log but try again
                log_prompt_and_response("practice_question_error", f"Topic: {topic_data['name']}, Attempt {attempt + 1}, Error: {e}")
                continue

        # If we couldn't generate a unique question after retries, log warning
        # The while loop will continue trying with other topics
        if not question_generated:
            log_prompt_and_response("question_generation_failed", f"Failed to generate unique question for {topic_data['name']} after {max_retries} attempts - will try different topic")

    # Final check: did we get the requested number?
    if len(questions) < num_questions:
        log_prompt_and_response("insufficient_questions", f"Only generated {len(questions)}/{num_questions} questions after {topic_iteration_count} topic attempts")
        # Still return what we have rather than failing completely
        if not questions:
            raise ValueError("Failed to generate any questions")

    return questions

__all__ = ['generate_grammar_question', 'generate_practice_session']

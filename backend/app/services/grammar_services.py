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

    enhanced_prompt = f"""You are an elementary‑level grammar tutor generating a multiple‑choice grammar question.

        Topic: {topic}
        Difficulty: {difficulty_text}

        Instructions:
        {prompt_template or 'N/A'}

        Examples:
        {example or 'N/A'}

        Question focus:
        {question_focus}

        Style constraints:
        {style_block}
        
        Required output rules:
        - Produce ONE multiple‑choice question only.
        - Include exactly FOUR answer choices.
        - DO NOT include fill‑in‑the‑blank questions.
        - DO NOT reveal the correct answer in the question stem.
        - Answer choices must be short, clear, and distinct.
        - Question must match the difficulty setting.
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

    # Generate questions for each selected topic
    questions = []
    for topic_data in selected_topics:
        try:
            result = generate_grammar_question(
                topic=topic_data['name'],
                subject='grammar',
                difficulty=difficulty,
                style=style
            )

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
        except Exception as e:
            # Log but continue with other questions
            log_prompt_and_response("practice_question_error", f"Topic: {topic_data['name']}, Error: {e}")
            continue

    if not questions:
        raise ValueError("Failed to generate any questions")

    return questions

__all__ = ['generate_grammar_question', 'generate_practice_session']

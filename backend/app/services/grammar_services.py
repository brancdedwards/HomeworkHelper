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
    definition = topic_data.get("definition")
    examples = topic_data.get("examples")

    if isinstance(examples, list):
        examples = "; ".join([x.strip() for x in examples])
    link = topic_data.get("link")

    if isinstance(definition, str):
        definition = definition.replace("\n", " ").strip()

    enhanced_prompt = f"""You are an elementary‑level grammar tutor generating a multiple‑choice grammar question.

        Topic: {topic}
        Difficulty: {difficulty_text}

        Definition:
        {definition or 'N/A'}

        Examples:
        {examples or 'N/A'}

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

    # Fixed call - matching the actual signature
    return generate_mcq_question(
        topic=topic,
        subject=subject,
        prompt_instructions=enhanced_prompt,
        source_prompt=enhanced_prompt  # Adding the missing parameter
    )
__all__ = ['generate_grammar_question']

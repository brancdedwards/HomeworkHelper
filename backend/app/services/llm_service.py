"""
llm_service.py
Business logic for question generation:
- Fetch prompt templates
- Build system/user prompts
- Call llm_client
- Guarantee N usable questions
"""

from backend.app.clients.llm_client import call_llm_json
from backend.db.session import get_db
from backend.app.schemas.questions import (
    question_from_llm_json,
    QuestionResponse,
    MULTIPLE_CHOICE_JSON_SCHEMA,
)
from backend.app.core import settings


def generate_mcq_question(topic: str, subject: str, prompt_instructions: str, source_prompt: str):
    """
    Generate a structured multiple-choice question using the JSON schema.
    """

    prompt = f"""
        You are a friendly, patient 5th‑grade tutor.
        Create ONE multiple‑choice question.
        
        Topic: {topic}
        Subject: {subject}
        
        
        Instructions:
        {prompt_instructions}
        
        Return ONLY JSON matching this schema:
        {MULTIPLE_CHOICE_JSON_SCHEMA['schema']}
        """

    # get JSON from LLM
    raw = call_llm_json(prompt, MULTIPLE_CHOICE_JSON_SCHEMA)
    if raw is None:
        raise ValueError("LLM returned no valid JSON.")

    # normalize → Pydantic model
    mcq = question_from_llm_json(raw)

    # wrap response
    return QuestionResponse(
        question=mcq,
        source_topic=topic,
        source_prompt=source_prompt,
        llm_model=settings.LLM_MODEL,
    )


def get_prompt_for_topic(topic: str):
    """Fetch prompt template + example from the topics table."""
    with get_db() as db:
        row = db.execute(
            "SELECT prompt_template, example FROM topics WHERE name = ?",
            (topic,)
        ).fetchone()

        if not row:
            return None, None

        return row["prompt_template"], row["example"]
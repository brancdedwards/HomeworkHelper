from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from backend.app.services.grammar_services import generate_grammar_question, generate_practice_session
# from backend.app.services.hint_service import get_hint_for_topic   # TODO: Fix imports
from backend.app.core.logging_config import log_prompt_and_response

router = APIRouter(prefix="/grammar", tags=["Grammar"])

class GrammarRequest(BaseModel):
    topic: str
    subject: str = "grammar"
    difficulty: str = "normal"
    style: str = "default"

class PracticeSessionRequest(BaseModel):
    num_questions: int = Field(ge=1, le=10, description="Number of questions (1-10)")
    category: Optional[str] = Field(None, description="Specific category to focus on, or None for random")
    difficulty: str = Field("normal", description="Question difficulty level")
    style: str = Field("default", description="Question style")

class HintRequest(BaseModel):
    topic: str
    wrong_answer: str

@router.get("/categories")
def get_categories():
    """
    Get list of all available grammar categories.
    Returns unique categories from active topics.
    """
    from backend.db.session import get_db

    try:
        with get_db() as db:
            rows = db.execute("""
                SELECT DISTINCT category
                FROM topics
                WHERE active = 1
                  AND subject = 'grammar'
                  AND category IS NOT NULL
                ORDER BY category
            """).fetchall()

            # Normalize categories: replace underscores with spaces and remove duplicates
            raw_categories = [row['category'] for row in rows]
            normalized = {}
            for cat in raw_categories:
                # Normalize to spaces and title case
                normalized_cat = cat.replace('_', ' ').title()
                # Use the original value as the key for lookup
                if normalized_cat not in normalized:
                    normalized[normalized_cat] = cat

            # Return sorted unique categories
            categories = sorted(normalized.keys())

            return {
                "categories": categories,
                "count": len(categories)
            }

    except Exception as e:
        log_prompt_and_response("get_categories_error", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/practice/session")
def create_practice_session(payload: PracticeSessionRequest):
    """
    Generate a practice session with N questions (1-10).
    Questions can be from a specific category or random mix.
    Returns a list of questions ready for practice.
    """
    try:
        questions = generate_practice_session(
            num_questions=payload.num_questions,
            category=payload.category,
            difficulty=payload.difficulty,
            style=payload.style
        )

        return {
            "num_questions": len(questions),
            "category": payload.category or "random",
            "questions": questions
        }

    except Exception as e:
        log_prompt_and_response("practice_session_error", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
def generate_question(payload: GrammarRequest):
    try:
        result = generate_grammar_question(
            topic=payload.topic,
            subject=payload.subject,
            difficulty=payload.difficulty,
            style=payload.style
        )
        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate question")

        # Extract correct answer from options
        correct_answer = next((opt.text for opt in result.question.options if opt.is_correct), None)

        return {
            "topic": result.source_topic,
            "question": result.question.prompt,
            "options": [opt.text for opt in result.question.options],
            "correct_answer": correct_answer,
            "explanation": result.question.explanation
        }

    except Exception as e:
        log_prompt_and_response("grammar_router_error", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/test")
def generate_question_test(payload: GrammarRequest):
    """
    Debug endpoint to inspect the raw LLM prompt, response, and parsed output.
    Useful for troubleshooting grammar question generation.
    """
    try:
        # Generate question with full debug info from the service
        result = generate_grammar_question(
            topic=payload.topic,
            subject=payload.subject,
            difficulty=payload.difficulty,
            style=payload.style
        )

        return {
            "topic": payload.topic,
            "difficulty": payload.difficulty,
            "style": payload.style,
            "raw_prompt": result.raw_prompt if hasattr(result, "raw_prompt") else None,
            "raw_response": result.raw_response if hasattr(result, "raw_response") else None,
            "parsed_question": {
                "question": result.question,
                "options": result.options,
                "answer": result.answer
            }
        }

    except Exception as e:
        log_prompt_and_response("grammar_generate_test_error", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# TODO: Re-enable hint endpoints once hint_service imports are fixed
# @router.post("/hint")
# def get_hint(payload: HintRequest):
#     try:
#         hint = get_hint_for_topic(payload.topic, payload.wrong_answer)
#         return {"topic": payload.topic, "hint": hint}
#     except Exception as e:
#         log_prompt_and_response("grammar_hint_error", str(e))
#         raise HTTPException(status_code=500, detail=str(e))
#
# @router.post("/hint/test")
# def test_hint(payload: HintRequest):
#     """
#     Debug endpoint for testing hint generation.
#     Returns hint, topic metadata, and the wrong answer.
#     """
#     try:
#         hint = get_hint_for_topic(payload.topic, payload.wrong_answer)
#
#         # Pull full topic record for debugging
#         from backend.app.services.topic_service import get_topic_data
#         topic_data = get_topic_data(payload.topic, subject="grammar")
#         normalized_wrong = payload.wrong_answer.strip().lower()
#
#         return {
#             "topic": payload.topic,
#             "wrong_answer": payload.wrong_answer,
#             "normalized_wrong_answer": normalized_wrong,
#             "hint": hint,
#             "topic_data_used": topic_data
#         }
#
#     except Exception as e:
#         log_prompt_and_response("grammar_hint_test_error", str(e))
#         raise HTTPException(status_code=500, detail=str(e))
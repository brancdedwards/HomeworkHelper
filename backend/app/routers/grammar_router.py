from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.services.grammar_services import generate_grammar_question
from backend.app.services.hint_service import get_hint_for_topic   # create later
from backend.app.core.logging_config import log_prompt_and_response

router = APIRouter(prefix="/grammar", tags=["Grammar"])

class GrammarRequest(BaseModel):
    topic: str
    subject: str = "grammar"
    difficulty: str = "normal"
    style: str = "default"

class HintRequest(BaseModel):
    topic: str
    wrong_answer: str

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

        return {
            "topic": payload.topic,
            "question": result.question,
            "options": result.options,
            "answer": result.answer
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

@router.post("/hint")
def get_hint(payload: HintRequest):
    try:
        hint = get_hint_for_topic(payload.topic, payload.wrong_answer)
        return {"topic": payload.topic, "hint": hint}
    except Exception as e:
        log_prompt_and_response("grammar_hint_error", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hint/test")
def test_hint(payload: HintRequest):
    """
    Debug endpoint for testing hint generation.
    Returns hint, topic metadata, and the wrong answer.
    """
    try:
        hint = get_hint_for_topic(payload.topic, payload.wrong_answer)

        # Pull full topic record for debugging
        from backend.app.services.topic_service import get_topic_data
        topic_data = get_topic_data(payload.topic, subject="grammar")
        normalized_wrong = payload.wrong_answer.strip().lower()

        return {
            "topic": payload.topic,
            "wrong_answer": payload.wrong_answer,
            "normalized_wrong_answer": normalized_wrong,
            "hint": hint,
            "topic_data_used": topic_data
        }

    except Exception as e:
        log_prompt_and_response("grammar_hint_test_error", str(e))
        raise HTTPException(status_code=500, detail=str(e))